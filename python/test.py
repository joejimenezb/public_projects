def removeDuplicates( nums) -> int:
        dist = 0
        for i in range(1, len(nums)):
            print(i)
            print(f"nums[i]:{nums[i]} == nums[i-1]:{nums[i-1]}  ")
            if nums[i] == nums[i-1]:
                dist += 1
            else:
                nums[i-dist] = nums[i]
        print(nums)
        return len(nums) - dist


t = [0,0,1,1,1,2,2,3,3,4]
print(removeDuplicates(t))