"Neogram: Gantt chart."

from icecream import ic

import datetime

from diagram import *
import utils


__all__ = ["Gantt", "Task"]


class Gantt(Diagram):
    "Gantt chart."

    DEFAULT_WIDTH = 500

    def __init__(
        self,
        id=None,
        klass=None,
        style=None,
        width=None,
        date_based=True,
        tasks=None,
    ):
        assert width is None or isinstance(width, (int, float))
        assert tasks is None or isinstance(tasks, (tuple, list))
        super().__init__(id=id, klass=klass, style=style)
        self.width = width if width is not None else self.DEFAULT_WIDTH
        self.date_based = date_based
        self.tasks = []
        if tasks:
            for task in tasks:
                self.append(task)

    def append(self, task):
        if isinstance(task, Task):
            item = task
        elif isinstance(task, (tuple, list)) and len(task) >= 3:
            item = Task(*task[:4])
        elif isinstance(task, dict) and len(task) >= 3:
            item = Task(
                label=task["label"],
                start=task["start"],
                finish=task["finish"],
                style=task.get("style"),
            )
        else:
            raise ValueError("invalid task specification")
        if self.date_based and not isinstance(task.start, datetime.date):
            raise ValueError("wrong type of 'start'/'finish' for this chart")
        self.tasks.append(item)

    def __iadd__(self, other):
        self.append(other)
        return self

    def viewbox(self):
        height = 0
        lanes = set()
        for task in self.tasks:
            if task.lane in lanes:
                continue
            height += task.height + 2 * self.style["padding"]
            lanes.add(task.lane)
        return (
            Vector2(0, 0),
            Vector2(self.width, height)
        )

    def svg_content(self):
        "Return the SVG content element in minixml representation."
        result = super().svg_content()
        self.style.setattrs(result, "stroke", "stroke-width", "fill")
        padding = self.style["padding"]
        rounded = self.style["rounded"]
        first = self.tasks[0].start
        last = self.tasks[0].finish
        for task in self.tasks[1:]:
            first = min(first, task.start)
            last = max(last, task.finish)
        scale_factor = self.width / (last - first)
        ymax = 0
        lanes = dict()
        for task in self.tasks:
            if task.lane in lanes:
                continue
            ymax += self.style["padding"]
            lanes[task.lane] = ymax
            ymax += task.height + self.style["padding"]
        xticks = [
            scale_factor * (tick - first) for tick in utils.get_ticks(first, last)
        ]
        path = Path(Vector2(xticks[0], 0))
        path.V(ymax)
        for xtick in xticks[1:]:
            path.M(Vector2(xtick, 0)).V(ymax)
        result += Element("path", d=path)
        labels = []
        for task in self.tasks:
            rect = Element(
                "rect",
                x=scale_factor * (task.start - first),
                y=lanes[task.lane],
                width=scale_factor * (task.finish - task.start),
                height=task.height,
                rx=rounded,
                ry=rounded,
            )
            if task.style:
                task.style.setattrs(rect, "stroke", "stroke-width", "fill")
            result += rect
            if task.label:
                label = Element(
                    "text",
                    x=scale_factor * ((task.start + task.finish) / 2 - first),
                    y=lanes[task.lane] + task.height - padding,
                )
                background = rect.get("fill") or result["fill"]
                self.style.setattrs_text(label, background=background)
                if task.style:  # Use task styles, if given.
                    task.style.setattrs_text(label, background=background)
                label += task.label
                labels.append(label)
        # Allow labels to overwrite anything prior.
        for label in labels:
            result += label
        return result

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        data = super().as_dict_content()
        data["tasks"] = [task.as_dict() for task in self.tasks]
        return data


add_diagram(Gantt)


class Task:
    "Task to be part of a Gantt chart."

    DEFAULT_HEIGHT = 16

    def __init__(self, label, start, finish, height=None, lane=None, style=None):
        assert label and isinstance(label, str)
        assert isinstance(start, (int, float, str, datetime.date))
        assert type(start) == type(finish)
        assert height is None or isinstance(height, (int, float))
        assert lane is None or isinstance(lane, str)
        self.label = label
        if isinstance(start, (int, float, datetime.date)):
            self.start = start
            self.finish = finish
        elif isinstance(start, str):
            self.start = datetime.date.fromisoformat(start)
            self.finish = datetime.date.fromisoformat(finish)
        assert self.start <= self.finish
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.lane = lane if lane is not None else self.label
        self.style = style

    def as_dict(self):
        data = dict(label=self.label)
        if isinstance(self.start, datetime.date):
            data["start"] = self.start.isoformat()
            data["finish"] = self.finish.isoformat()
        else:
            data["start"] = self.start
            data["finish"] = self.finish
        data["height"] = self.height
        return {"task": data}
