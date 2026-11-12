# Days 15-21: data structures and algorithms, one small idea per screen. Exec'd inside lessons.py (helpers exist).

# ------------------------------------------------------------------ Day 15
LESSONS[15] = [
 S("Big-O: count the steps, not the seconds",
   "Interviewers ask \"how does it scale?\". <b>Complexity</b> is how the number of steps grows when the input grows. Seconds depend on your laptop; steps do not. Below, <code>steps</code> counts one step per item looked at.",
   '''def count_steps(items):
    steps = 0
    for x in items:
        steps = steps + 1
    return steps

print(count_steps([5, 6, 7]))
print(count_steps(list(range(1000))))''', run=True,
   q=Q("What does this show?", '''steps = 0
for x in [4, 8, 15, 16]:
    steps = steps + 1
print(steps)''', ["4", "1", "43"], "The loop body runs once per item, and there are 4 items. Twice as many items would mean twice as many steps.")),
 S("O(1) and O(n)",
   "<b>O(1)</b> (\"constant\") means the work does not grow with the input: looking at <code>xs[0]</code> takes one step for 10 items or 10 million. <b>O(n)</b> (\"linear\") means the work grows in step with the input: <code>sum(xs)</code> must touch every item. The letter n just means \"how many items\".",
   '''xs = list(range(1000))
print(xs[0])      # O(1): one step
print(sum(xs))    # O(n): 1000 steps''', run=True,
   q=QC("Which of these is O(1)?", ["Reading xs[3] from a list", "Adding up every number in a list", "Checking whether a value is anywhere in a list"], 0, "Jumping straight to a position costs one step, whatever the length. The other two may have to visit every item.")),
 S("O(n^2): a loop inside a loop",
   "A loop inside a loop gives <b>O(n^2)</b> (\"quadratic\"): for every item you walk the whole list again. Ten items means about 100 steps; a thousand items means a million. That is why interviewers push you away from nested loops.",
   '''def count_pairs(items):
    steps = 0
    for a in items:
        for b in items:
            steps = steps + 1
    return steps

print(count_pairs([1, 2, 3]))
print(count_pairs(list(range(10))))''', run=True,
   q=Q("What does this show?", '''steps = 0
for a in range(4):
    for b in range(4):
        steps = steps + 1
print(steps)''', ["16", "8", "4"], "4 outer rounds, each with 4 inner rounds: 4 x 4 = 16. Double the input to 8 and it would be 64.")),
 S("O(log n): halving",
   "<b>O(log n)</b> (\"logarithmic\") means each step throws away half of what is left. A million items need only about 20 halvings. You will use this in binary search. By feel, from fastest to slowest: <b>O(1), O(log n), O(n), O(n^2)</b>.",
   '''n = 16
steps = 0
while n > 1:
    n = n // 2
    steps = steps + 1
print(steps)''', run=True,
   q=Q("What does this show?", '''n = 64
steps = 0
while n > 1:
    n = n // 2
    steps = steps + 1
print(steps)''', ["6", "64", "32"], "64 -> 32 -> 16 -> 8 -> 4 -> 2 -> 1 is six halvings. Doubling the input only added one step.")),
 S("A list searches one by one; a set jumps",
   "<code>x in my_list</code> may compare against every item: O(n). <code>x in my_set</code> (or in a dict) uses a <b>hash</b>: the value is turned into a number that says where to look, so it finds it in about one step, O(1). Anything built on a hash, like a set or dict, is called a <b>hash map</b> or hash table. The cost: it uses extra memory.",
   '''def list_lookup_steps(items, target):
    steps = 0
    for x in items:
        steps = steps + 1
        if x == target:
            break
    return steps

big = list(range(1000))
print(list_lookup_steps(big, 999))   # list: 1000 comparisons
print(999 in set(big))               # set: jumps straight there''', run=True,
   q=QC("You will ask \"have I seen this id?\" a million times. Why is a set much faster than a list?", ["A set jumps to the spot using a hash instead of checking items one by one", "A set keeps its items sorted so it can stop early", "A set stores fewer items than a list"], 0, "Hashing turns the value into a location. A list has no such shortcut, so its check grows with its length.")),
 S("Two-sum: slow way first",
   "Classic question: given numbers and a target, find the two positions whose values add up to the target. The brute force tries every pair with two loops: O(n^2). It works, but it will time out on big inputs.",
   '''def two_sum_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

print(two_sum_slow([2, 7, 11, 15], 9))''', run=True,
   q=Q("What does this show?", '''def two_sum_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []

print(two_sum_slow([3, 2, 4], 6))''', ["[1, 2]", "[0, 0]", "[]"], "3+2 is 5 and 3+4 is 7, neither is 6. Then 2+4 is 6, which is positions 1 and 2.")),
 S("Two-sum: fast way with a dict",
   "Instead of searching for a partner, <b>remember</b> what you have passed. For each number, the partner you need is <code>target - num</code>. Ask the dict (value -> position): \"have I already seen that partner?\" One pass, O(n). You trade memory for speed.",
   '''def two_sum(nums, target):
    seen = {}                      # value -> position
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

print(two_sum([2, 7, 11, 15], 9))
print(two_sum([1, 2], 10))''', run=True,
   q=Q("What does this show?", '''def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        need = target - num
        if need in seen:
            return [seen[need], i]
        seen[num] = i
    return []

print(two_sum([3, 3], 6))''', ["[0, 1]", "[]", "[1, 1]"], "At position 0 the dict is empty, so 3 is stored. At position 1 the partner 3 is already in the dict at position 0, giving [0, 1].")),
 S("Frequency counting",
   "Counting how often each thing appears (the Day 4 pattern) is the second most common hashing trick. Two words are <b>anagrams</b> if they use the same letters the same number of times, so equal counts means anagram. <code>Counter</code> from Day 6 does the counting.",
   '''from collections import Counter

def is_anagram(a, b):
    return Counter(a) == Counter(b)

print(is_anagram("listen", "silent"))
print(is_anagram("abc", "abd"))
print(Counter("banana"))''', run=True,
   q=Q("What does this show?", '''from collections import Counter
c = Counter("mississippi")
print(c["s"], c["p"])''', ["4 2", "2 4", "4 4"], "mississippi has four s and two p.")),
 S("Your turn: two-sum with a dict",
   "Same shape as the example, now typed by you. Remember: for each number, look for <code>target - num</code> in the dict, otherwise store this number's position.",
   q=W("Write <code>two_sum(nums, target)</code> that returns a list of the two positions <code>[i, j]</code> (smaller position first) whose values add up to <code>target</code>, or <code>[]</code> if there is no such pair. Use a dict so it is one pass.",
       "def two_sum(nums, target):\n    seen = {}\n    # for each position and value:\n    #   work out the partner you need\n    #   if the partner is in seen, return [its position, this position]\n    #   otherwise store this value's position\n    pass\n",
       "def two_sum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        need = target - num\n        if need in seen:\n            return [seen[need], i]\n        seen[num] = i\n    return []",
       exprs=["two_sum([2, 7, 11, 15], 9)", "two_sum([3, 2, 4], 6)", "two_sum([3, 3], 6)", "two_sum([1, 2], 10)", "two_sum([], 5)", "two_sum([5], 5)", "two_sum([-1, -2, -3, -4, -5], -8)", "two_sum([0, 4, 0], 0)"],
       hint="seen[num] = i stores a value's position. Check 'need in seen' before you store, so a number is not paired with itself.")),
]

# ------------------------------------------------------------------ Day 16
LESSONS[16] = [
 S("Pair with a target sum: the slow way",
   "Problem: in a <b>sorted</b> list, is there a pair that adds up to a target? Brute force checks every pair: O(n^2). Keep it in mind; we are about to beat it.",
   '''def has_pair_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

print(has_pair_slow([1, 3, 4, 6, 9], 10))
print(has_pair_slow([1, 3, 4, 6, 9], 2))''', run=True,
   q=Q("What does this show?", '''def has_pair_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False

print(has_pair_slow([2, 5, 8], 13))''', ["True", "False", "13"], "5 + 8 is 13, so a pair exists.")),
 S("Two pointers: start at both ends",
   "A <b>pointer</b> is just a variable holding a position (an index). Put one at the start (<code>left</code>) and one at the end (<code>right</code>). Add the two values. Too small? Move <code>left</code> right to get a bigger number. Too big? Move <code>right</code> left. Each step throws one position away, so it is O(n). This only works because the list is sorted.",
   '''def has_pair(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        print(left, right, total)
        if total == target:
            return True
        if total < target:
            left = left + 1
        else:
            right = right - 1
    return False

print(has_pair([1, 3, 4, 6, 9], 10))''', run=True,
   q=Q("What does this show?", '''nums = [1, 3, 4, 6, 9]
left, right = 0, 4
total = nums[left] + nums[right]
if total > 7:
    right = right - 1
print(left, right)''', ["0 3", "1 4", "0 4"], "1 + 9 = 10 is bigger than 7, so we need a smaller number and the right pointer moves left.")),
 S("Why does moving a pointer never miss the answer?",
   "Think about it before you answer. In a sorted list, if <code>nums[left] + nums[right]</code> is too small, then <code>nums[left]</code> paired with <i>anything</i> to its left of <code>right</code> is even smaller (those numbers are no bigger than <code>nums[right]</code>). So <code>nums[left]</code> can never be part of the answer, and we can safely drop it.",
   q=QC("What breaks the two-pointer method for pair-sum?", ["The list is not sorted", "The list has an even number of items", "The target is negative"], 0, "The whole argument relies on sorted order: moving a pointer must reliably make the sum bigger or smaller. Without sorting (or with a hash set, Day 15) you need another approach.")),
 S("Two pointers also checks palindromes",
   "A <b>palindrome</b> reads the same backwards (\"level\"). Compare the first and last characters, then move both pointers inwards. Stop when they meet. Any mismatch means False.",
   '''def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left = left + 1
        right = right - 1
    return True

print(is_palindrome("level"))
print(is_palindrome("abca"))''', run=True,
   q=Q("What does this show?", '''def is_palindrome(s):
    left, right = 0, len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left = left + 1
        right = right - 1
    return True

print(is_palindrome("noon"), is_palindrome(""))''', ["True True", "True False", "False True"], "noon matches from both ends. The empty string has left=0, right=-1, so the loop never runs and it returns True.")),
 S("Sliding window: a fixed-size slice that moves",
   "A <b>window</b> is a slice of k neighbouring items. Task: the biggest sum of any 3 neighbours. The slow way adds up each window from scratch: O(n x k).",
   '''def best_sum_slow(nums, k):
    best = sum(nums[:k])
    for i in range(len(nums) - k + 1):
        best = max(best, sum(nums[i:i + k]))
    return best

print(best_sum_slow([2, 1, 5, 1, 3, 2], 3))''', run=True,
   q=Q("What does this show?", 'print(max(sum([1, 2, 3]), sum([2, 3, 4]), sum([3, 4, 1])))', ["9", "6", "8"], "The sums are 6, 9 and 8; the biggest is 9.")),
 S("Slide: add the new item, drop the old one",
   "When the window moves one step, only two things change: one item enters on the right and one leaves on the left. So update the running sum with <code>+ new - old</code> instead of re-adding k numbers. Now it is O(n).",
   '''def best_sum(nums, k):
    window = sum(nums[:k])
    best = window
    for i in range(k, len(nums)):
        window = window + nums[i] - nums[i - k]
        best = max(best, window)
    return best

print(best_sum([2, 1, 5, 1, 3, 2], 3))''', run=True,
   q=QC("Why is the sliding window faster than adding up every window from scratch?", ["Each move reuses the previous sum and does one add and one subtract", "It skips every second window", "It sorts the list first"], 0, "Neighbouring windows share k-1 items. Reusing their sum means constant work per move instead of k.")),
 S("Variable window: grow and shrink",
   "Sometimes the window size is not fixed. Example: the longest run of neighbours (all positive numbers) whose sum stays <= a limit. Move <code>right</code> to grow the window. If it gets too heavy, move <code>left</code> forward to shrink it until it fits. Both pointers only ever move forward, so it is O(n).",
   '''def longest_run(nums, limit):
    left = 0
    total = 0
    best = 0
    for right in range(len(nums)):
        total = total + nums[right]
        while total > limit:
            total = total - nums[left]
            left = left + 1
        best = max(best, right - left + 1)
    return best

print(longest_run([2, 1, 3, 1, 1], 5))''', run=True,
   q=Q("What does this show?", '''def longest_run(nums, limit):
    left = 0
    total = 0
    best = 0
    for right in range(len(nums)):
        total = total + nums[right]
        while total > limit:
            total = total - nums[left]
            left = left + 1
        best = max(best, right - left + 1)
    return best

print(longest_run([4, 1, 1, 1, 4], 3))''', ["3", "5", "2"], "The run 1, 1, 1 sums to 3, which fits, and no longer run fits under 3.")),
 S("Which pattern when?",
   "A quick decision rule for interviews: <b>sorted</b> data and a pair or a meeting point -> two pointers. <b>Contiguous</b> chunk (substring or subarray) of a size or limit -> sliding window. Unsorted and \"have I seen the partner?\" -> hash map (Day 15).",
   q=QC("\"Find the longest substring of a string that has no repeated letter.\" Which pattern fits best?", ["Sliding window (a contiguous chunk that grows and shrinks)", "Binary search", "Sorting the string, then two pointers from both ends"], 0, "A substring is contiguous, and you grow it until a repeat appears, then shrink from the left. Sorting would destroy the order of the letters.")),
 S("Your turn: fixed sliding window",
   "Build the window sum once, then slide it.",
   q=W("Write <code>max_window_sum(nums, k)</code> that returns the biggest sum of any <code>k</code> neighbouring numbers. If <code>k</code> is less than 1 or bigger than the list length, return <code>0</code>. Slide the window; do not re-add every window.",
       "def max_window_sum(nums, k):\n    if k < 1 or k > len(nums):\n        return 0\n    # 1. sum the first k numbers\n    # 2. for each later position: add the new number, subtract the one that left\n    # 3. keep the biggest sum\n    pass\n",
       "def max_window_sum(nums, k):\n    if k < 1 or k > len(nums):\n        return 0\n    window = sum(nums[:k])\n    best = window\n    for i in range(k, len(nums)):\n        window = window + nums[i] - nums[i - k]\n        best = max(best, window)\n    return best",
       exprs=["max_window_sum([2, 1, 5, 1, 3, 2], 3)", "max_window_sum([1, 2, 3], 3)", "max_window_sum([-1, -2, -3, -4], 2)", "max_window_sum([7], 1)", "max_window_sum([], 1)", "max_window_sum([1, 2], 5)", "max_window_sum([4, -1, 2, -7, 5], 2)"],
       hint="window = window + nums[i] - nums[i - k] for i from k to the end. Negative numbers: start best from the first window, not from 0.")),
]

# ------------------------------------------------------------------ Day 17
LESSONS[17] = [
 S("A stack: last in, first out",
   "A <b>stack</b> is a pile of plates: you add to the top and take from the top, so the last one in is the first one out (<b>LIFO</b>). In Python a list is a stack: <code>append</code> pushes on, <code>pop()</code> takes the top one off and returns it. Both are O(1).",
   '''stack = []
stack.append("a")
stack.append("b")
stack.append("c")
print(stack.pop())
print(stack)''', run=True,
   q=Q("What does this show?", '''stack = [1, 2]
stack.append(3)
stack.pop()
stack.pop()
print(stack)''', ["[1]", "[1, 2]", "[3]"], "Pushing 3 gives [1, 2, 3]. Two pops remove 3 and then 2, leaving [1].")),
 S("The stack's classic job: matching brackets",
   "Is <code>(()())</code> properly closed? Every <code>(</code> must be matched by a later <code>)</code>. Push each opener. When a closer comes, the most recent opener is on top, so pop it. If you try to pop from an empty stack, or anything is left at the end, the brackets do not match.",
   '''def balanced(s):
    stack = []
    for ch in s:
        if ch == "(":
            stack.append(ch)
        elif ch == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

print(balanced("(()())"))
print(balanced("())"))
print(balanced("(("))''', run=True,
   q=Q("What does this show?", '''def balanced(s):
    stack = []
    for ch in s:
        if ch == "(":
            stack.append(ch)
        elif ch == ")":
            if not stack:
                return False
            stack.pop()
    return len(stack) == 0

print(balanced(")("))''', ["False", "True", "Error"], "The first character is a closer and the stack is empty, so it returns False at once.")),
 S("Several kinds of brackets",
   "With <code>( ) [ ] { }</code> a count is no longer enough, because <code>([)]</code> is wrong even though the counts match. Use a dict that maps each closer to its opener. When a closer arrives, the top of the stack must be its own opener.",
   '''def valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return len(stack) == 0

print(valid("{[()]}"))
print(valid("([)]"))''', run=True,
   q=Q("What does this show?", '''def valid(s):
    pairs = {")": "(", "]": "[", "}": "{"}
    stack = []
    for ch in s:
        if ch in pairs:
            if not stack or stack.pop() != pairs[ch]:
                return False
        else:
            stack.append(ch)
    return len(stack) == 0

print(valid("[](){}"), valid("(]"))''', ["True False", "True True", "False False"], "[](){} closes each bracket straight away. In (] the closer ] meets the opener ( on top, which does not match.")),
 S("Why a stack and not a counter?",
   "Brackets nest like boxes inside boxes: the <b>innermost</b> open one must close first. \"Most recent unfinished thing comes first\" is exactly last-in-first-out. Undo buttons, the back button and function calls (Day 18) work the same way.",
   q=QC("When is a stack the right tool?", ["When the most recent unfinished item must be handled first", "When you need the smallest item quickly", "When you need to look up a value by name"], 0, "Last-in-first-out matches nested or \"undo\" situations. Smallest-first is a heap (Day 20); lookup by name is a dict.")),
 S("Binary search: the idea",
   "Guess a number from 1 to 100; I say \"higher\" or \"lower\". Best strategy: always guess the middle, throwing away half. In a <b>sorted</b> list that is <b>binary search</b>: O(log n), so a million items take about 20 looks. The linear way checks one by one.",
   '''nums = list(range(0, 1000, 2))     # 500 sorted even numbers

def linear_steps(nums, target):
    steps = 0
    for x in nums:
        steps = steps + 1
        if x == target:
            break
    return steps

print(linear_steps(nums, 998))''', run=True,
   q=QC("Binary search needs the list to be...", ["Sorted", "Made only of whole numbers", "Shorter than 100 items"], 0, "Throwing away half only makes sense when sorted order tells you which half the target is in.")),
 S("Binary search in code: lo, hi, mid",
   "Keep two positions: <code>lo</code> (leftmost still possible) and <code>hi</code> (rightmost still possible). Look at <code>mid</code>, the middle. Equal: found. Target bigger: the answer is right of mid, so <code>lo = mid + 1</code>. Target smaller: <code>hi = mid - 1</code>. The <code>+ 1</code> and <code>- 1</code> matter: mid has already been checked.",
   '''def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        print("lo", lo, "hi", hi, "mid", mid)
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(binary_search([1, 3, 5, 7, 9, 11], 9))''', run=True,
   q=Q("What does this show?", '''nums = [10, 20, 30, 40, 50]
lo, hi = 0, 4
mid = (lo + hi) // 2
print(mid, nums[mid])''', ["2 30", "2 20", "3 40"], "(0 + 4) // 2 is 2, and the item at position 2 is 30.")),
 S("The off-by-one trap",
   "The most common binary search bug is the loop condition. With <code>while lo &lt; hi</code> the loop stops while <code>lo</code> and <code>hi</code> are the same position, which is still a candidate that was never checked. Use <code>lo &lt;= hi</code> when both ends are still possible answers. Run this broken version to see it miss a value that is really there.",
   '''def broken_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:               # bug: should be lo <= hi
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(broken_search([1, 3, 5, 7, 9], 9))
print(broken_search([1, 3, 5, 7, 9], 5))''', run=True,
   q=Q("What does the broken version print for the first target (the last item)?", '''def broken_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

print(broken_search([1, 3, 5, 7, 9], 9))''', ["-1", "4", "9"], "lo moves to 3 and then 4, equal to hi, and the loop ends before 9 at position 4 is ever checked. The correct condition is lo <= hi.")),
 S("When does binary search apply?",
   "Whenever there is a yes/no question that flips exactly once as you walk along an ordered range. The list is the obvious case, but it also solves \"smallest speed that finishes in time\" and similar problems.",
   q=QC("Why is binary search on 1,000,000 sorted items so much faster than a linear scan?", ["Each look discards half the remaining items, so about 20 looks are enough", "It checks several items at the same moment", "It only works on small lists"], 0, "Halving a million repeatedly reaches 1 in about 20 steps. A linear scan may need a million.")),
 S("Your turn: binary search",
   "Return the position of the target, or -1.",
   q=W("Write <code>binary_search(nums, target)</code> for a <b>sorted</b> list. Return the position of <code>target</code>, or <code>-1</code> if it is not there. Use <code>lo</code>, <code>hi</code>, <code>mid</code>; do not use <code>in</code> or <code>index</code>.",
       "def binary_search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    # while there is still a range left (lo <= hi):\n    #   look at the middle\n    #   found -> return its position\n    #   too small -> lo = mid + 1;  too big -> hi = mid - 1\n    pass\n",
       "def binary_search(nums, target):\n    lo, hi = 0, len(nums) - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        if nums[mid] == target:\n            return mid\n        if nums[mid] < target:\n            lo = mid + 1\n        else:\n            hi = mid - 1\n    return -1",
       exprs=["binary_search([1, 3, 5, 7, 9, 11], 7)", "binary_search([1, 3, 5, 7, 9, 11], 1)", "binary_search([1, 3, 5, 7, 9, 11], 11)", "binary_search([1, 3, 5, 7, 9, 11], 4)", "binary_search([], 3)", "binary_search([5], 5)", "binary_search([5], 6)", "binary_search([-9, -4, 0, 3], -4)"],
       hint="Use while lo <= hi. After a miss, move lo to mid + 1 or hi to mid - 1.")),
]

# ------------------------------------------------------------------ Day 18
LESSONS[18] = [
 S("A linked list: items that point to the next",
   "A list stores items side by side. A <b>linked list</b> stores each item in a small object called a <b>node</b>, and each node holds a pointer (a reference) to the next node. The last node points to <code>None</code>. You only hold the first node, the <b>head</b>, and follow the chain.",
   '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = Node(1, Node(2, Node(3)))
print(head.val)
print(head.next.val)
print(head.next.next.next)''', run=True,
   q=Q("What does this show?", '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = Node(10, Node(20, Node(30)))
print(head.next.next.val)''', ["30", "20", "None"], "head.next is the 20 node, and its next is the 30 node.")),
 S("Walking the chain",
   "To visit every node: keep a variable <code>cur</code> that starts at the head, and keep moving it with <code>cur = cur.next</code> until it becomes <code>None</code>. This is a <code>while</code> loop, because you do not know the length in advance.",
   '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = Node(4, Node(5, Node(6)))
cur = head
while cur is not None:
    print(cur.val)
    cur = cur.next''', run=True,
   q=Q("What does this show?", '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = Node(1, Node(2, Node(3, Node(4))))
total = 0
cur = head
while cur:
    total = total + cur.val
    cur = cur.next
print(total)''', ["10", "4", "6"], "The loop visits 1, 2, 3 and 4 and adds them.")),
 S("Why have linked lists at all?",
   "Putting a new node at the very front is O(1): make a node that points at the old head. A normal list has to shift every item along: O(n). The price: you cannot jump to the 500th item; you must walk 500 steps (O(n)).",
   '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

head = Node(2, Node(3))
head = Node(1, head)      # add at the front: no shifting

cur = head
out = []
while cur:
    out.append(cur.val)
    cur = cur.next
print(out)''', run=True,
   q=QC("Which is cheaper on a linked list than on a plain list?", ["Inserting a new item at the front", "Reading the item at position 500", "Checking the length"], 0, "Front insertion changes one pointer. Reaching position 500 needs 500 hops.")),
 S("Reversing a list: three variables",
   "Reverse by turning every arrow around as you walk. You need <code>prev</code> (the node behind, starts as None), <code>cur</code> (the node you are on) and <code>nxt</code> (saved before you break the link, or you would lose the rest of the chain). Each round: save next, point cur backwards, step both forward.",
   '''class Node:
    def __init__(self, val, next=None):
        self.val = val
        self.next = next

def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    return prev

new_head = reverse(Node(1, Node(2, Node(3))))
while new_head:
    print(new_head.val)
    new_head = new_head.next''', run=True,
   q=QC("Why save <code>nxt = cur.next</code> before changing <code>cur.next</code>?", ["Once cur.next points backwards, the rest of the chain would be lost", "Python requires a new variable for every pointer change", "It makes the loop run faster"], 0, "Overwriting cur.next removes your only way forward, so you must remember it first.")),
 S("Recursion: a function that calls itself",
   "<b>Recursion</b> solves a problem by solving a smaller copy of it. Every recursive function needs a <b>base case</b>: the smallest version, answered directly with no further call. Without it, it would call itself forever. Here, counting down to 1.",
   '''def countdown(n):
    if n == 0:             # base case: stop
        print("go")
        return
    print(n)
    countdown(n - 1)       # smaller problem

countdown(3)''', run=True,
   q=Q("What does this show?", '''def countdown(n):
    if n == 0:
        print("go")
        return
    print(n)
    countdown(n - 1)

countdown(2)''', ["2\n1\ngo", "go\n1\n2", "2\n1"], "countdown(2) prints 2 and calls countdown(1), which prints 1 and calls countdown(0), which prints go.")),
 S("The call stack: Python remembers where each call is",
   "Each call waits for the call below it. Python keeps these waiting calls in a <b>call stack</b> (the stack from Day 17!). Factorial: <code>n! = n x (n-1)!</code>, with <code>0! = 1</code> as the base case. The calls go down, then the answers come back up.",
   '''def fact(n):
    if n == 0:
        return 1
    print("fact", n, "waiting for fact", n - 1)
    result = n * fact(n - 1)
    print("fact", n, "returns", result)
    return result

print(fact(3))''', run=True,
   q=Q("What does this show?", '''def fact(n):
    if n == 0:
        return 1
    return n * fact(n - 1)

print(fact(5))''', ["120", "25", "15"], "5 x 4 x 3 x 2 x 1 = 120, with fact(0) = 1 ending the chain.")),
 S("No base case: the stack overflows",
   "If you forget the base case, the calls pile up until Python stops you with a <b>RecursionError</b> (the stack has a depth limit, around 1000). When you see that error, check: is there a base case, and does every call really get smaller?",
   q=QE("What happens when this runs?", '''def count(n):
    return count(n - 1) + 1

print(count(3))''', "RecursionError", ["It prints 3", "It prints 0", "RecursionError: the function never stops calling itself"], 2, "count(3) calls count(2), then count(1), count(0), count(-1) and so on, never reaching a stopping point.")),
 S("Fibonacci, and the repeated work problem",
   "Fibonacci: each number is the sum of the previous two (0, 1, 1, 2, 3, 5, 8...). The recursive version is short but recomputes the same values again and again. <code>calls</code> counts how often the function runs.",
   '''calls = 0

def fib(n):
    global calls
    calls = calls + 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10))
print(calls)''', run=True,
   q=Q("Memoization means saving each answer in a dict the first time it is computed. How many calls does this memoised version make for fib(10)?", '''calls = 0
memo = {}

def fib(n):
    global calls
    calls = calls + 1
    if n < 2:
        return n
    if n in memo:
        return memo[n]
    memo[n] = fib(n - 1) + fib(n - 2)
    return memo[n]

fib(10)
print(calls)''', ["19", "177", "10"], "Each value is computed once and then looked up. The plain version needed 177 calls for the same answer. Memoising turns exponential work into O(n).")),
 S("Your turn: reverse a linked list",
   "The <code>Node</code> class and two helpers (<code>build</code> makes a chain from a list, <code>to_list</code> reads one back) are already defined for you.",
   q=W("Write <code>reverse_list(head)</code> that reverses a linked list and returns the new head. An empty list (<code>None</code>) stays <code>None</code>.",
       "def reverse_list(head):\n    prev = None\n    cur = head\n    # while cur:\n    #   save cur.next\n    #   point cur.next at prev\n    #   move prev and cur forward\n    # return prev\n    pass\n",
       "def reverse_list(head):\n    prev = None\n    cur = head\n    while cur:\n        nxt = cur.next\n        cur.next = prev\n        prev = cur\n        cur = nxt\n    return prev",
       exprs=["to_list(reverse_list(build([1, 2, 3])))", "to_list(reverse_list(build([1, 2, 3, 4, 5])))", "to_list(reverse_list(build([7])))", "reverse_list(None)", "to_list(reverse_list(build([1, 2])))", "to_list(reverse_list(build([5, 5, 6])))"],
       prelude="class Node:\n    def __init__(self, val, next=None):\n        self.val = val\n        self.next = next\n\ndef build(items):\n    head = None\n    for v in reversed(items):\n        head = Node(v, head)\n    return head\n\ndef to_list(head):\n    out = []\n    while head:\n        out.append(head.val)\n        head = head.next\n    return out\n",
       hint="Inside the loop, in order: nxt = cur.next, cur.next = prev, prev = cur, cur = nxt.")),
]

# ------------------------------------------------------------------ Day 19
LESSONS[19] = [
 S("A tree: nodes with children",
   "A <b>tree</b> is a node (the <b>root</b>) with up to two <b>children</b>, <code>left</code> and <code>right</code>, each of which is itself a tree. Nodes with no children are <b>leaves</b>. It is like a linked list, but each node can point two ways.",
   '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

#       1
#      / \\
#     2   3
root = TreeNode(1, TreeNode(2), TreeNode(3))
print(root.val, root.left.val, root.right.val)
print(root.left.left)''', run=True,
   q=Q("What does this show?", '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

root = TreeNode(5, TreeNode(3, TreeNode(1)), TreeNode(8))
print(root.left.left.val + root.right.val)''', ["9", "8", "4"], "root.left.left is the 1 node and root.right is the 8 node: 1 + 8 = 9.")),
 S("Recursion fits trees perfectly",
   "A tree is a node with smaller trees hanging off it, so a recursive function fits naturally. Base case: no node (<code>None</code>). Otherwise: answer = combine the answers for the left and right subtrees. <b>Depth</b> (how many levels) = 1 + the deeper of the two sides.",
   '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def depth(node):
    if node is None:
        return 0
    return 1 + max(depth(node.left), depth(node.right))

root = TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))
print(depth(root))
print(depth(None))''', run=True,
   q=Q("What does this show?", '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def count(node):
    if node is None:
        return 0
    return 1 + count(node.left) + count(node.right)

print(count(TreeNode(1, TreeNode(2), TreeNode(3, TreeNode(4)))))''', ["4", "3", "2"], "Each of the four nodes contributes 1, and None contributes 0.")),
 S("DFS: go deep first",
   "<b>DFS</b> (depth-first search) follows one branch all the way down before backing up. The order you print relative to the recursive calls gives the classic orders. Printing the node <i>before</i> its children is \"preorder\"; between the left and right is \"inorder\".",
   '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def preorder(node):
    if node is None:
        return
    print(node.val)
    preorder(node.left)
    preorder(node.right)

root = TreeNode(1, TreeNode(2, TreeNode(4)), TreeNode(3))
preorder(root)''', run=True,
   q=Q("What does this show (inorder: left, then node, then right)?", '''class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def inorder(node, out):
    if node is None:
        return
    inorder(node.left, out)
    out.append(node.val)
    inorder(node.right, out)

out = []
inorder(TreeNode(2, TreeNode(1), TreeNode(3)), out)
print(out)''', ["[1, 2, 3]", "[2, 1, 3]", "[3, 2, 1]"], "Left first (1), then the node (2), then right (3).")),
 S("A graph: things connected to things",
   "A <b>graph</b> is nodes joined by edges: cities and roads, people and friendships. A tree is a graph with no loops. The easiest way to store one is an <b>adjacency dict</b>: each node maps to the list of its neighbours.",
   '''graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D"],
    "D": [],
}
print(graph["A"])
print(len(graph["D"]))''', run=True,
   q=Q("What does this show?", '''graph = {1: [2, 3], 2: [4], 3: [], 4: [1]}
print(graph[graph[1][0]])''', ["[4]", "[2, 3]", "[1]"], "graph[1][0] is 2, and graph[2] is [4].")),
 S("BFS: spread out level by level",
   "<b>BFS</b> (breadth-first search) visits all neighbours first, then their neighbours, like ripples in water. It uses a <b>queue</b>: first in, first out (the opposite of a stack). Python's <code>deque</code> from <code>collections</code> gives O(1) <code>popleft()</code>; a plain list's <code>pop(0)</code> is O(n).",
   '''from collections import deque

graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}

queue = deque(["A"])
order = []
while queue:
    node = queue.popleft()
    order.append(node)
    for nb in graph[node]:
        queue.append(nb)
print(order)''', run=True,
   q=Q("What does this show?", '''from collections import deque
q = deque([1, 2])
q.append(3)
print(q.popleft(), q.popleft())''', ["1 2", "3 2", "2 1"], "A queue hands out the oldest item first: 1, then 2.")),
 S("The visited set stops endless loops",
   "In the last example, D was added twice, because both B and C lead to it. With a loop in the graph (A -> B -> A) the search would never end. Keep a <code>visited</code> set: mark a node when you first see it and never queue it again.",
   '''from collections import deque

graph = {"A": ["B", "C"], "B": ["A", "D"], "C": ["D"], "D": []}

visited = {"A"}
queue = deque(["A"])
order = []
while queue:
    node = queue.popleft()
    order.append(node)
    for nb in graph[node]:
        if nb not in visited:
            visited.add(nb)
            queue.append(nb)
print(order)''', run=True,
   q=QC("Why mark a node as visited at the moment it is added to the queue?", ["So it is never queued twice and loops cannot go on forever", "So BFS runs in reverse", "Because a set sorts the nodes for you"], 0, "Marking at queue time guarantees every node is processed once. Checking membership in a set is O(1).")),
 S("BFS finds the shortest path (fewest steps)",
   "Because BFS explores in rings, the first time it reaches a node is by the fewest steps. Store the distance with each node. <b>DFS</b> dives deep and may find a long route first, so for \"fewest steps\" in an unweighted graph choose BFS; for \"explore everything / does a path exist\", either works.",
   '''from collections import deque

graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": ["E"], "E": []}

dist = {"A": 0}
queue = deque(["A"])
while queue:
    node = queue.popleft()
    for nb in graph[node]:
        if nb not in dist:
            dist[nb] = dist[node] + 1
            queue.append(nb)
print(dist)''', run=True,
   q=Q("What does this show?", '''from collections import deque

graph = {1: [2, 3], 2: [4], 3: [4], 4: [5], 5: []}
dist = {1: 0}
queue = deque([1])
while queue:
    node = queue.popleft()
    for nb in graph[node]:
        if nb not in dist:
            dist[nb] = dist[node] + 1
            queue.append(nb)
print(dist[5])''', ["3", "4", "2"], "1 -> 2 -> 4 -> 5 is three steps.")),
 S("A grid is a graph too",
   "A grid of 0s and 1s is a graph: each cell's neighbours are up, down, left and right. Counting <b>islands</b> (groups of touching 1s): scan the grid; when you meet an unvisited 1, count one island and use DFS to mark the whole island visited.",
   '''def count_islands(grid):
    rows, cols = len(grid), len(grid[0])
    seen = set()

    def dfs(r, c):
        if r < 0 or c < 0 or r >= rows or c >= cols:
            return
        if grid[r][c] == 0 or (r, c) in seen:
            return
        seen.add((r, c))
        dfs(r + 1, c)
        dfs(r - 1, c)
        dfs(r, c + 1)
        dfs(r, c - 1)

    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1 and (r, c) not in seen:
                islands = islands + 1
                dfs(r, c)
    return islands

print(count_islands([[1, 1, 0], [0, 0, 1], [1, 0, 1]]))''', run=True,
   q=QC("In count_islands, why is the check <code>r &lt; 0 or c &lt; 0 or r &gt;= rows or c &gt;= cols</code> first?", ["It is the base case: it stops the recursion at the edge of the grid", "It sorts the grid", "It counts the islands"], 0, "Stepping outside the grid must stop without reading grid[r][c], which would be an error or a wrong wrap-around.")),
 S("Your turn: shortest path with BFS",
   "Use the BFS-with-distance pattern from earlier.",
   q=W("Write <code>shortest_steps(graph, start, goal)</code>. <code>graph</code> is an adjacency dict. Return the fewest edges needed to get from <code>start</code> to <code>goal</code>, or <code>-1</code> if it cannot be reached. Use BFS with a <code>deque</code>.",
       "from collections import deque\n\ndef shortest_steps(graph, start, goal):\n    dist = {start: 0}\n    queue = deque([start])\n    # while the queue has nodes:\n    #   take the oldest one; if it is the goal return its distance\n    #   for each neighbour not yet in dist: record dist + 1 and queue it\n    pass\n",
       "from collections import deque\n\ndef shortest_steps(graph, start, goal):\n    dist = {start: 0}\n    queue = deque([start])\n    while queue:\n        node = queue.popleft()\n        if node == goal:\n            return dist[node]\n        for nb in graph[node]:\n            if nb not in dist:\n                dist[nb] = dist[node] + 1\n                queue.append(nb)\n    return -1",
       exprs=["shortest_steps({1: [2, 3], 2: [4], 3: [4], 4: []}, 1, 4)", "shortest_steps({1: [2], 2: [3], 3: []}, 1, 1)", "shortest_steps({1: [2], 2: [], 3: []}, 1, 3)", "shortest_steps({1: [2, 3], 2: [1, 4], 3: [1], 4: []}, 3, 4)", "shortest_steps({'a': ['b'], 'b': ['c'], 'c': ['a']}, 'a', 'c')", "shortest_steps({1: []}, 1, 1)"],
       hint="Return dist[node] when node == goal. Only queue a neighbour that is not in dist yet.")),
]

# ------------------------------------------------------------------ Day 20
LESSONS[20] = [
 S("A heap: the smallest is always ready",
   "A <b>heap</b> is a list arranged so the smallest item can be taken out quickly. Python's <code>heapq</code> module makes a plain list behave as a <b>min-heap</b>: <code>heappush</code> adds an item, <code>heappop</code> removes and returns the smallest. Each is O(log n), far cheaper than re-sorting every time.",
   '''import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 8)
print(heapq.heappop(h))
print(heapq.heappop(h))
print(len(h))''', run=True,
   q=Q("What does this show?", '''import heapq
h = [4, 9, 2]
heapq.heapify(h)
print(heapq.heappop(h), heapq.heappop(h))''', ["2 4", "4 9", "9 4"], "heapify arranges an existing list into a heap. Pops always give the smallest next: 2, then 4.")),
 S("The k largest: nlargest",
   "<code>heapq.nlargest(k, items)</code> and <code>nsmallest</code> return the k biggest or smallest in order. For small k on a huge list this beats sorting everything (O(n log k) instead of O(n log n)), and it is the standard \"top K\" tool.",
   '''import heapq

scores = [50, 91, 73, 88, 62]
print(heapq.nlargest(2, scores))
print(heapq.nsmallest(2, scores))''', run=True,
   q=QC("When is a heap a better choice than sorting the whole list?", ["You only need the top few items, or items keep arriving and you always want the smallest", "You need every item in order, once", "The list is already sorted"], 0, "A heap keeps only what you need. If you want everything sorted once, plain sorting is simpler.")),
 S("Heaps of tuples: priorities",
   "Put <code>(priority, name)</code> tuples in a heap. Tuples compare left to right, so the smallest priority comes out first, with the name breaking ties. This is a to-do list that always hands you the most urgent task.",
   '''import heapq

tasks = []
heapq.heappush(tasks, (3, "write report"))
heapq.heappush(tasks, (1, "fix outage"))
heapq.heappush(tasks, (2, "reply to email"))

while tasks:
    priority, name = heapq.heappop(tasks)
    print(priority, name)''', run=True,
   q=Q("What does this show?", '''import heapq
h = []
heapq.heappush(h, (2, "b"))
heapq.heappush(h, (2, "a"))
heapq.heappush(h, (1, "z"))
print(heapq.heappop(h)[1], heapq.heappop(h)[1])''', ["z a", "z b", "a b"], "(1, 'z') is smallest. Then both remaining tuples have priority 2, so the names decide and 'a' comes before 'b'.")),
 S("Intervals: when do two ranges overlap?",
   "An <b>interval</b> is a range like <code>[1, 4]</code> (start, end). Two intervals overlap when the second one starts before (or when) the first one ends. Meeting-room and calendar problems are interval problems. First, put them in order of start time.",
   '''meetings = [[8, 10], [1, 3], [2, 6]]
meetings.sort()
print(meetings)

a, b = [1, 3], [2, 6]
print(b[0] <= a[1])     # does b start before a ends?''', run=True,
   q=Q("What does this show?", '''a, b = [1, 3], [4, 6]
print(b[0] <= a[1])''', ["False", "True", "4"], "b starts at 4 but a ended at 3, so there is a gap.")),
 S("Why sort first?",
   "To merge overlapping intervals, sort them by start. After sorting, any interval that overlaps the last merged one must start at or before that one ends, so you only ever compare with the <b>last</b> merged interval, never the whole list. Without sorting, you would have to compare every pair: O(n^2).",
   q=QC("After sorting by start, what is enough to check when adding the next interval?", ["Only whether it overlaps the last merged interval", "Whether it overlaps every earlier interval", "Whether its end is bigger than all other ends"], 0, "Sorted order means later starts are never earlier than previous ones, so only the most recent merged interval can overlap it.")),
 S("DP intro: a problem made of smaller copies",
   "<b>Dynamic programming</b> (DP) means: solve a big problem from answers to smaller versions of itself, and never solve the same small problem twice. Climbing stairs: you can take 1 or 2 steps at a time; how many ways to reach step n? To reach step n you came from step n-1 or n-2, so <code>ways(n) = ways(n-1) + ways(n-2)</code>. The base cases: 1 way to stay at the bottom, 1 way to reach step 1.",
   '''calls = 0

def ways(n):
    global calls
    calls = calls + 1
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)

print(ways(5))
print(calls)''', run=True,
   q=Q("What does this show?", '''def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)

print(ways(4))''', ["5", "4", "8"], "ways(2)=2, ways(3)=3, ways(4)=5. The ways are 1111, 112, 121, 211, 22.")),
 S("Memoization: remember answers",
   "The plain recursion recalculates <code>ways(2)</code> over and over. Fix: a dict called a <b>memo</b>. Before computing, check the memo; after computing, store the answer. This is called <b>top-down</b> DP: it starts with the big question and recurses down.",
   '''calls = 0
memo = {}

def ways(n):
    global calls
    calls = calls + 1
    if n <= 1:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = ways(n - 1) + ways(n - 2)
    return memo[n]

print(ways(30))
print(calls)''', run=True,
   q=Q("What does this show?", '''memo = {}
def ways(n):
    if n <= 1:
        return 1
    if n in memo:
        return memo[n]
    memo[n] = ways(n - 1) + ways(n - 2)
    return memo[n]

ways(10)
print(len(memo))''', ["9", "10", "11"], "The memo stores n = 2 to 10, which is nine entries (n = 0 and 1 hit the base case).")),
 S("Table: fill from the bottom up",
   "<b>Bottom-up</b> DP skips recursion: build a table where <code>table[i]</code> is the answer for step i, starting from the base cases and filling upward. Each cell is computed once from earlier cells. The same idea works for the coin problem: fewest coins to make an amount, where <code>table[a] = 1 + min(table[a - coin])</code>.",
   '''def ways(n):
    table = [1] * (n + 1)          # table[0] = table[1] = 1
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table[n]

print(ways(5))
print(ways(30))''', run=True,
   q=Q("What does this show?", '''def ways(n):
    table = [1] * (n + 1)
    for i in range(2, n + 1):
        table[i] = table[i - 1] + table[i - 2]
    return table

print(ways(5))''', ["[1, 1, 2, 3, 5, 8]", "[1, 2, 3, 4, 5]", "[1, 1, 1, 1, 1, 1]"], "Each cell is the sum of the two before it, starting from 1, 1.")),
 S("Your turn: merge intervals",
   "Sort, then walk through, either extending the last merged interval or starting a new one.",
   q=W("Write <code>merge_intervals(intervals)</code>. Given a list of <code>[start, end]</code> pairs in any order, return a list of merged pairs sorted by start. Intervals that overlap or touch (next start &lt;= previous end) are merged. For <code>[[1,3],[2,6],[8,10]]</code> return <code>[[1, 6], [8, 10]]</code>.",
       "def merge_intervals(intervals):\n    if not intervals:\n        return []\n    # 1. sort by start\n    # 2. merged = [first interval]\n    # 3. for each next interval: if it starts <= last merged end, extend the end (use max)\n    #    otherwise append it as a new interval\n    pass\n",
       "def merge_intervals(intervals):\n    if not intervals:\n        return []\n    items = sorted([list(p) for p in intervals])\n    merged = [items[0]]\n    for start, end in items[1:]:\n        if start <= merged[-1][1]:\n            merged[-1][1] = max(merged[-1][1], end)\n        else:\n            merged.append([start, end])\n    return merged",
       exprs=["merge_intervals([[1, 3], [2, 6], [8, 10]])", "merge_intervals([[8, 10], [1, 3], [2, 6]])", "merge_intervals([[1, 4], [4, 5]])", "merge_intervals([[1, 10], [2, 3]])", "merge_intervals([])", "merge_intervals([[5, 6]])", "merge_intervals([[1, 2], [3, 4]])"],
       hint="Compare start with merged[-1][1]. When merging, the new end is max(old end, end), because the later interval may sit inside the earlier one.")),
]

# ------------------------------------------------------------------ Day 21
LESSONS[21] = [
 S("Mock interview step 1: read and restate",
   "In a timed round the first two minutes decide the rest. Read the problem twice. Then say it back in your own words: what goes in, what comes out, what counts as valid input? Ask about edge cases out loud (empty input? duplicates? negatives?). Interviewers score this heavily, and it prevents solving the wrong problem.",
   q=QC("You get: \"Return the indices of two numbers that add to a target.\" What is the best first move?", ["Restate it and ask: can there be duplicates, no answer, negative numbers? Is the list sorted?", "Start typing a nested loop right away", "Ask the interviewer to give you the solution"], 0, "Clarifying inputs, outputs and edge cases costs one minute and often changes which pattern fits (sorted -> two pointers, unsorted -> hash map).")),
 S("Step 2: brute force first, then improve",
   "Always say the simple correct solution first, even if slow: \"I can check every pair, that is O(n^2).\" It proves you understand the problem and gives you a baseline. Then ask: <b>what work is repeated?</b> Repeated searching -> hash map. Repeated re-summing -> sliding window. Repeated sorted-order scanning -> two pointers or binary search.",
   '''def has_duplicate_slow(nums):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return True
    return False

def has_duplicate_fast(nums):
    seen = set()
    for x in nums:
        if x in seen:
            return True
        seen.add(x)
    return False

data = [4, 1, 7, 1]
print(has_duplicate_slow(data), has_duplicate_fast(data))''', run=True,
   q=QC("In has_duplicate_slow, which repeated work does the set remove?", ["Searching the rest of the list again for every number", "Sorting the list", "Reading the input"], 0, "The slow version re-scans the remaining items for each number. A set answers \"seen it?\" in one step.")),
 S("Step 3: test by hand before you say \"done\"",
   "Walk a small example through your code, line by line, writing the variables down. Then try the awkward inputs: empty, one item, all the same, negatives, target not found. Most interview bugs are off-by-one (like <code>lo &lt; hi</code> vs <code>lo &lt;= hi</code>) or a forgotten empty case, and tracing finds them before the interviewer does.",
   '''def last_index(nums, target):
    pos = -1
    for i in range(len(nums)):
        if nums[i] == target:
            pos = i
    return pos

# test the awkward cases, not just the happy one
print(last_index([1, 2, 1], 1))
print(last_index([], 1))
print(last_index([5], 9))''', run=True,
   q=Q("Trace it. What does this show?", '''def last_index(nums, target):
    pos = -1
    for i in range(len(nums)):
        if nums[i] == target:
            pos = i
    return pos

print(last_index([3, 3, 3], 3), last_index([3, 4], 4))''', ["2 1", "0 1", "2 0"], "With three 3s, pos is overwritten each time, ending at 2. In [3, 4], the 4 is at position 1.")),
 S("Step 4: state the complexity",
   "Finish every answer with <b>time</b> (how steps grow) and <b>space</b> (how much extra memory). Rules of thumb: one loop is O(n); a loop inside a loop is O(n^2); halving is O(log n); sorting is O(n log n); a set or dict adds O(n) space.",
   q=QC("Which description fits this code?<pre>def f(nums):\n    seen = set()\n    for x in nums:\n        if x in seen:\n            return True\n        seen.add(x)\n    return False</pre>", ["Time O(n), space O(n)", "Time O(n^2), space O(1)", "Time O(log n), space O(1)"], 0, "One pass, with O(1) set operations, gives O(n) time. The set can grow to hold every item, which is O(n) space.")),
 S("Mixed review: which pattern is this?",
   "Eight patterns from this week, one line each: hash map (seen it / counting), two pointers (sorted pair), sliding window (contiguous chunk), stack (nested, undo), binary search (sorted, halve), linked list pointers, recursion on trees/DFS, BFS (fewest steps), heap (top k), sort-then-sweep (intervals), DP (overlapping subproblems).",
   q=Q("Predict the output (a sliding window plus a set):", '''s = "abcabcbb"
seen = set()
left = 0
best = 0
for right in range(len(s)):
    while s[right] in seen:
        seen.remove(s[left])
        left = left + 1
    seen.add(s[right])
    best = max(best, right - left + 1)
print(best)''', ["3", "8", "4"], "The longest stretch with no repeated letter is abc, length 3. The window shrinks from the left whenever a repeat appears.")),
 S("Final mock task: top K frequent",
   "A real interview-style problem. Restate it, think brute force, then improve. Plan: <b>count</b> with a dict (hash map), then <b>sort</b> the distinct values by count (highest first, smaller value first on a tie) and take the first k.",
   q=W("Write <code>top_k_frequent(nums, k)</code>. Return a list of the <code>k</code> most frequent numbers, most frequent first. If two numbers have the same count, the smaller number comes first. If <code>k</code> is more than the number of distinct values, return them all. Empty input gives <code>[]</code>.",
       "def top_k_frequent(nums, k):\n    # 1. count each number with a dict\n    # 2. sort the distinct numbers by (-count, number)\n    # 3. return the first k\n    pass\n",
       "def top_k_frequent(nums, k):\n    counts = {}\n    for n in nums:\n        counts[n] = counts.get(n, 0) + 1\n    ordered = sorted(counts, key=lambda n: (-counts[n], n))\n    return ordered[:k]",
       exprs=["top_k_frequent([1, 1, 1, 2, 2, 3], 2)", "top_k_frequent([4], 1)", "top_k_frequent([], 3)", "top_k_frequent([5, 3, 5, 3, 1], 2)", "top_k_frequent([-1, -1, 2, 2, 3], 3)", "top_k_frequent([7, 8, 8], 10)", "top_k_frequent([1, 2, 3], 0)"],
       hint="sorted(counts, key=lambda n: (-counts[n], n)) orders by highest count first, then smaller number. Then slice [:k].")),
]
