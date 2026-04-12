nums = list(range(1, 1001))

# We want to get 20 elements starting from 500 but by skipping 2 elements in the middle
# 500, 503, 506, 509, .... til 20 times
start_index = 0
end_index = 0

for i in range(0, len(nums)):
  if nums[i] == 500:
    start_index = i
    break

end_index = start_index + (20 * 3)

print(nums[start_index : end_index : 3])

