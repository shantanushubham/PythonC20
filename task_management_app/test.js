const myPromise = new Promise((resolve, reject) => {
  setTimeout(() => {
    resolve("Shantanu Shubham")
  }, 2 * 1000)
})

function addTwoNumbers(a, b) {
  return a + b;
}

myPromise.then((data) => {
  console.log(`The name is: ${data}`)
})

const sum = addTwoNumbers(5, 6)
console.log(`The sum is: ${sum}`)
