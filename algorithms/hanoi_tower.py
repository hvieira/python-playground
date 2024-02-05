from typing import List, Dict
from dataclasses import dataclass, field


@dataclass
class HanoiTower:
    source_peg: List[int]
    source_peg_label: str = "A"

    auxiliary_peg: List[int] = field(default_factory=list)
    auxiliary_peg_label = "B"

    target_peg: List[int] = field(default_factory=list)
    target_peg_label = "C"

    label_to_peg: Dict[str, List[int]] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.label_to_peg[self.source_peg_label] = self.source_peg
        self.label_to_peg[self.auxiliary_peg_label] = self.auxiliary_peg
        self.label_to_peg[self.target_peg_label] = self.target_peg

    def move_disk_between_pegs(self, from_peg_label, to_peg_label):
        # this would need validating here (target peg is empty or top disk is of bigger value )
        disk = self.label_to_peg[from_peg_label].pop()
        self.label_to_peg[to_peg_label].append(disk)
        print(f"move disk {disk} from {from_peg_label} to {to_peg_label}")
        return HanoiMove(disk, from_peg_label, to_peg_label)

    def moves_to_solve(self):
        def solve(num_disks, source_peg, auxiliary_peg, target_peg, moves):
            if num_disks > 0:
                print(f"goal is moving {num_disks} disks from {source_peg} to {target_peg}")
                # solve the problem by placing the upper disks in the auxiliary peg
                solve(num_disks-1, source_peg=source_peg, auxiliary_peg=target_peg, target_peg=auxiliary_peg, moves=moves)

                # move this disk (largest for the problem) to the target peg    
                moves.append(self.move_disk_between_pegs(source_peg, target_peg))

                # move the disks we moved before to the auxiliary peg to the target
                solve(num_disks-1, source_peg=auxiliary_peg, auxiliary_peg=source_peg, target_peg=target_peg, moves=moves)

            return moves

        return solve(
            len(self.source_peg),
            self.source_peg_label,
            self.auxiliary_peg_label,
            self.target_peg_label,
            [],
        )

        # return [self.move_disk_between_pegs(from_peg_label=self.source_peg_label, to_peg_label=self.target_peg_label)]


@dataclass
class HanoiMove:
    disk: int
    from_peg: str
    to_peg: str
