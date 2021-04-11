from dataclasses import dataclass, field
from random import shuffle, randint
from typing import Any, List, Tuple

import argh
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from numpy import float64, ndarray
from pandas.core.frame import DataFrame
from rich import inspect
from rich import print as p
from rich import traceback
from rich.console import Console
from rich.progress import track

# Global console for pretty printing and traceback for better debugging
console = Console()
traceback.install()


@dataclass
class Student():
    times_heard: int = field(default=0)
    _able_to_spread: bool = field(default=True)

    def heard(self):
        return self.times_heard > 0

    def able_to_tell(self):
        return self.heard() and self._able_to_spread

    def hear(self):
        self.times_heard += 1
        if self.times_heard >= 2:
            self._able_to_spread = False

    def tell(self, other):
        # if self.heard() and not self.stop_spreading:
        # if not self.stop_spreading:
        # if self.able_to_tell():
        if randint(0, 1):
            other.hear()


def main(student_cnt: int = 2, stop_time: int = 100, display: bool = False):
    assert student_cnt >= 2 and student_cnt <= 10000
    students = [Student() for _ in range(student_cnt)]
    students[0].hear()

    def amount_heard():
        return sum([s.heard() for s in students])

    time = 0
    # Simulation Loop
    # stop_time = 2
    if display:
        console.rule(f'cnt={student_cnt}, stop={stop_time}')
    while time < stop_time:
        if display:
            p(amount_heard())

        shuffle(students)
        split = student_cnt//2
        firsts = students[:split]
        seconds = students[split:]

        for i in range(len(firsts)):
            first = firsts[i]
            second = seconds[i]

            # if first.able_to_tell():
            #     first.tell(second)
            # elif second.able_to_tell():
            #     second.tell(first)

            if first.able_to_tell() and second.able_to_tell():
                first.hear()
                second.hear()
            elif first.able_to_tell():
                first.tell(second)
            elif second.able_to_tell():
                second.tell(first)

        time += 1

    # Every person who has knowledge of the rumor obeys these rules:
    # 1. The likelihood of spreading a rumor to another person is 0.5
    # 2. After a person has heard the rumor 2 times, he/she will assume
    # everyone has heard the rumor and will no longer try to spread it further.

    # return (amount_heard / student_cnt) * 100
    return (amount_heard() / student_cnt)


def avg_main(student_cnt: int = 2, stop_time: int = 100, trials: int = 10):
    tot = 0
    for t in range(trials):
        tot += main(student_cnt, stop_time)
    tot /= trials
    return tot


def experiment():
    inds = [100, 1000, 10000]
    # data = [[main(n, 10), main(n, 20), main(n, 40)] for n in inds]
    data = [[avg_main(n, 10), avg_main(n, 20), avg_main(n, 40)] for n in inds]
    cols = [10, 20, 40]
    df = pd.DataFrame(data, columns=cols, index=inds)
    p(df)
    with console.status('Plotting'):
        sns.set()
        ax = sns.heatmap(df, annot=True)
        ax.invert_yaxis()
        plt.title('Rumor Spread vs. Time')
        plt.xlabel('Maximum Minutes')
        plt.ylabel('Student Count')
        plt.tight_layout()  # type: ignore
        plt.show()


# run your simulation several times to determine:
# 1. On average, what % of the attendees will have heard the rumor after 10 minutes?
# 2. On average, what % of the attendees will have heard the rumor after 20 minutes?
# 3. On average, what % of the attendees will have heard the rumor after 40 minutes?
# 4. At what time, t, will 10 % of the party have heard the rumor? N = 10, 000.
# 5. At what time, t, will 50 % of the party have heard the rumor? N = 10, 000.

if __name__ == '__main__':
    argh.dispatch_commands([main, experiment])
