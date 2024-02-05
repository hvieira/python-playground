num_disks=4
A = list(range(num_disks,0,-1))
B = []
C = []

# The smallest problem would be a single disk -> all recurse calls to move would be NOOP and just move the single disk from source to target
# the 2nd smallest problem - 2 disks:
# - move the smallest disk to auxilary; it follows the pattern above, but the target is the auxiliary instead of the target
# - move the largest disk (2) to target
# - move back the smallest disk from auxiliary to target
# the 3rd smallest problem - 3 disks:
# - once we get to situation where we've achived the solution for 2 disks, target being the auxiliary for these:
#   - move largest disk to target
#   - run the 2 disk problem from source B (original auxiliary, where we said we wanted to put all disks above the largest) to target C (original target), using A as auxiliary (original source) which is now empty
# Ultimately the idea is:
# 1. solve the problem for all disks above the largest one, but the target for those being the auxiliary peg
# 2. move the largest disk to the target peg
# 3. Solve the problem for the disks in auxiliary (N-1) peg to target peg, using the source (now empty as auxiliary)

def move(n, source, target, auxiliary):
    if n > 0:
        # Move n - 1 disks from source to auxiliary, so they are out of the way 
        # i.e. move disks that are on top of the largest one to the auxiliary peg, 
        # so that we can then move the largest disk - N'th disk) to the target)
        move(n - 1, source=source, target=auxiliary, auxiliary=target)

        # Move the nth disk from source to target
        disk = source.pop()
        peg = "A" if target is A else "B" if target is B else "C"
        print(f"moving {disk} to {peg}")
        target.append(disk)

        # Display our progress
        print(A, B, C, '##############', sep='\n')

        # Move the n - 1 disks that we left on auxiliary onto target
        move(n - 1, source=auxiliary, target=target, auxiliary=source)

# Initiate call from source A to target C with auxiliary B
move(num_disks, source=A, target=C, auxiliary=B)