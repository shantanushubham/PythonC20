// Graceful shutdown demo client.
//
// Usage:
//
//	# Terminal 1 — start the server
//	uvicorn task_app.asgi:application --timeout-graceful-shutdown 30
//
//	# Terminal 2 — fire slow demo requests
//	go run .
//
// While requests are in-flight, press Ctrl+C in Terminal 1.
// Requests already sleeping should complete with 200; new ones fail to connect.
package main

import (
	"bytes"
	"context"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/signal"
	"sync"
	"sync/atomic"
	"syscall"
	"time"
)

func main() {
	url := flag.String("url", "http://localhost:8000/api/demo/graceful-shutdown/", "slow demo endpoint")
	seconds := flag.Float64("seconds", 5, "seconds the server sleeps per request")
	workers := flag.Int("workers", 5, "concurrent request workers")
	interval := flag.Duration("interval", 500*time.Millisecond, "delay between requests per worker")
	duration := flag.Duration("duration", 0, "how long to run (0 = until Ctrl+C)")
	requestTimeout := flag.Duration("timeout", 60*time.Second, "per-request HTTP timeout")
	flag.Parse()

	client := &http.Client{Timeout: *requestTimeout}

	ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
	defer stop()

	if *duration > 0 {
		var cancel context.CancelFunc
		ctx, cancel = context.WithTimeout(ctx, *duration)
		defer cancel()
	}

	var (
		requestID atomic.Int64
		okCount   atomic.Int64
		errCount  atomic.Int64
		startedAt = time.Now()
		wg        sync.WaitGroup
	)

	fmt.Println("Graceful shutdown demo — slow request load generator")
	fmt.Printf("  url       : %s\n", *url)
	fmt.Printf("  seconds   : %.1f\n", *seconds)
	fmt.Printf("  workers   : %d\n", *workers)
	fmt.Printf("  interval  : %s\n", *interval)
	fmt.Printf("  timeout   : %s\n", *requestTimeout)
	fmt.Println()
	fmt.Println("Press Ctrl+C here to stop the client.")
	fmt.Println("Press Ctrl+C on the server while requests are sleeping to demo graceful shutdown.")
	fmt.Println()

	for worker := 1; worker <= *workers; worker++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				default:
				}

				id := requestID.Add(1)
				sendRequest(ctx, client, workerID, id, *url, *seconds, &okCount, &errCount)

				select {
				case <-ctx.Done():
					return
				case <-time.After(*interval):
				}
			}
		}(worker)
	}

	<-ctx.Done()
	fmt.Println()
	fmt.Println("Stopping workers, waiting for in-flight requests...")
	wg.Wait()

	elapsed := time.Since(startedAt).Round(time.Millisecond)
	fmt.Println()
	fmt.Printf("Done in %s — ok: %d, errors: %d\n", elapsed, okCount.Load(), errCount.Load())
}

func sendRequest(
	ctx context.Context,
	client *http.Client,
	workerID int,
	id int64,
	url string,
	seconds float64,
	okCount, errCount *atomic.Int64,
) {
	start := time.Now()
	requestLabel := fmt.Sprintf("demo-%04d", id)

	body, err := json.Marshal(map[string]float64{"seconds": seconds})
	if err != nil {
		errCount.Add(1)
		fmt.Printf("[#%04d worker=%02d] marshal body error: %v\n", id, workerID, err)
		return
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewReader(body))
	if err != nil {
		errCount.Add(1)
		fmt.Printf("[#%04d worker=%02d] build request error: %v\n", id, workerID, err)
		return
	}
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("X-Request-Id", requestLabel)

	fmt.Printf("[#%04d worker=%02d] START %s (sleep %.1fs)\n", id, workerID, requestLabel, seconds)

	resp, err := client.Do(req)
	elapsed := time.Since(start).Round(time.Millisecond)

	if err != nil {
		errCount.Add(1)
		fmt.Printf("[#%04d worker=%02d] ERROR after %s — %v\n", id, workerID, elapsed, err)
		return
	}
	defer resp.Body.Close()

	respBody, _ := io.ReadAll(io.LimitReader(resp.Body, 256))
	if resp.StatusCode >= 200 && resp.StatusCode < 300 {
		okCount.Add(1)
	} else {
		errCount.Add(1)
	}
	fmt.Printf("[#%04d worker=%02d] %d %s in %s — %s\n",
		id, workerID, resp.StatusCode, http.StatusText(resp.StatusCode), elapsed, truncate(string(respBody), 120))
}

func truncate(s string, max int) string {
	if len(s) <= max {
		return s
	}
	return s[:max] + "..."
}
