from dataclasses import dataclass, field
from random import shuffle, randint
from typing import Any, List, Optional, Tuple

import argh
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.core.indexes.base import Index
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
        if randint(0, 1):
            other.hear()


def main(student_cnt: int = 2, stop_time: int = 2000, stop_percent: Optional[float] = None, display: bool = False):
    assert student_cnt >= 2 and student_cnt <= 10000
    students = [Student() for _ in range(student_cnt)]
    students[0].hear()

    if display:
        console.rule(f'cnt={student_cnt}, stop={stop_time}')

    def percent_heard():
        return sum([s.heard() for s in students]) / student_cnt

    time = 0
    while time < stop_time:
        shuffle(students)
        split = student_cnt//2
        firsts = students[:split]
        seconds = students[split:]

        for i in range(len(firsts)):
            first = firsts[i]
            second = seconds[i]

            if first.able_to_tell() and second.able_to_tell():
                if randint(0, 1):
                    first.hear()
                if randint(0, 1):
                    second.hear()
            elif first.able_to_tell():
                first.tell(second)
            elif second.able_to_tell():
                second.tell(first)

        time += 1
        if stop_percent is not None:
            if percent_heard() >= stop_percent:
                break

        if display:
            p(time, percent_heard)

    return percent_heard(), time


def avg_main_time(student_cnt: int = 2, stop_time: int = 100, trials: int = 10):
    tot = 0.0
    for t in track(range(trials), description=f'Trials (students={student_cnt}, max_time={stop_time}) '):
        tot += main(student_cnt, stop_time)[0]
    tot /= trials
    return tot


def avg_main_percent(student_cnt: int = 2, stop_percent: float = 1.0, trials: int = 10):
    tot = 0.0
    for t in track(range(trials), description=f'Trials (students={student_cnt}, stop_percent={stop_percent}) '):
        tot += main(student_cnt, stop_percent=stop_percent)[1]
    tot /= trials
    return tot


def experiment(trials: int = 100, run_max_time: bool = False, run_max_percent: bool = False):
    if run_max_time:
        console.rule('[bold blue] Maximum Time')
        inds = [100, 1000, 10000]
        cols = [10, 20, 40]
        data = [[avg_main_time(n, 10, trials), avg_main_time(n, 20, trials),
                 avg_main_time(n, 40, trials)] for n in inds]
        df = pd.DataFrame(data, columns=cols, index=inds)

        with console.status('Plotting'):
            def percent(x):
                return f'{(x*100):0.2f}%'
            annots = [[percent(col) for col in row] for row in data]

            sns.set()
            ax = sns.heatmap(df, annot=annots, fmt='')
            ax.invert_yaxis()
            plt.title(f'Rumor Spread vs. Time (Avgeraged over {trials} trials)')
            plt.xlabel('Maximum Minutes')
            plt.ylabel('Student Count')
            plt.tight_layout()  # type: ignore
            plt.show()

            sns.lineplot(data=df.T)
            plt.title(f'Rumor Spread over time for different Student Counts \n(Avgeraged over {trials} trials)')
            plt.xlabel('Minutes')
            plt.legend(title='Student Count')   # type: ignore
            plt.ylabel('Rumor Spread %')
            plt.tight_layout()  # type: ignore
            plt.show()

    if run_max_percent:
        console.rule('[bold blue] Maximum Percent')
        inds = [100, 1000, 10000]
        cols = ['10%', '50%']
        data = [[avg_main_percent(n, .10, trials), avg_main_percent(n, .50, trials)] for n in inds]
        df = pd.DataFrame(data, columns=cols, index=inds)

        with console.status('Plotting'):
            sns.set()

            annots = [[str(col) for col in row] for row in data]
            # ax = sns.heatmap(df, annot=annots, fmt='')
            ax = sns.heatmap(df, annot=True)
            ax.invert_yaxis()

            plt.title(f'Minutes till Percentage Reached\n(Avgeraged over {trials} trials)')
            plt.xlabel('Target Percentage')
            plt.ylabel('Student Count')
            plt.tight_layout()  # type: ignore
            plt.show()

            sns.lineplot(data=df.T)
            plt.title(f'Rumor Spread over time for different Student Counts \n(Avgeraged over {trials} trials)')
            plt.xlabel('Target Percentage')
            plt.legend(title='Student count')   # type: ignore
            plt.ylabel('Minutes taken')
            plt.tight_layout()  # type: ignore
            plt.show()

if __name__ == '__main__':
    argh.dispatch_commands([main, experiment])
