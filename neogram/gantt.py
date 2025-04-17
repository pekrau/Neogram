"Neogram: Gantt chart."

from icecream import ic

import datetime

from diagram import *
import utils


__all__ = ["Gantt", "Task"]


class Gantt(Diagram):
    "Gantt chart."

    DEFAULT_WIDTH = 500
    DEFAULT_STYLE = Style(
        stroke=Color("black"),
        stroke_width=1,
        fill=Color("yellow"),
        width=16,
        padding=2,
        round=2,
        text=dict(size=14, anchor="middle", font="sans-serif"),
    )

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
            item = Task(label=task["label"],
                        start=task["start"],
                        finish=task["finish"],
                        style=task.get("style"))
        else:
            raise ValueError("invalid task specification")
        if self.date_based and not isinstance(task.start, datetime.date):
            raise ValueError("wrong type of 'start'/'finish' for this chart")
        self.tasks.append(item)

    def __iadd__(self, other):
        self.append(other)
        return self

    def viewbox(self):
        return (Vector2(0, 0),
                Vector2(
                    self.width,
                    len(self.tasks) * (self.style["width"] + 2 * self.style["padding"])
                )
                )

    def svg_content(self):
        "Return the SVG content element in minixml representation."
        result = super().svg_content()
        self.style.setattrs(result, "stroke", "stroke-width", "fill")
        width = self.style["width"]
        padding = self.style["padding"]
        r = self.style["round"]
        first = self.tasks[0].start
        last = self.tasks[0].finish
        for task in self.tasks[1:]:
            first = min(first, task.start)
            last = max(last, task.finish)
        scale_factor = self.width / (last - first)
        ymax = len(self.tasks) * (width + 2 * padding)
        xticks = [scale_factor * (tick - first) for tick in utils.get_ticks(first, last)]
        path = Path(Vector2(xticks[0], 0))
        path.V(ymax)
        for xtick in xticks[1:]:
            path.M(Vector2(xtick, 0)).V(ymax)
        result += Element("path", d=path)
        for pos, task in enumerate(self.tasks):
            rect = Element("rect",
                           x=scale_factor * (task.start - first),
                           y=pos * (width + 2 * padding) + padding,
                           width=scale_factor * (task.finish - task.start),
                           height=width,
                           rx=r,
                           ry=r,
                           )
            if task.style:
                task.style.setattrs(rect, "stroke", "stroke-width", "fill")
            result += rect
            if task.label:
                label = Element("text",
                                x=scale_factor * ((task.start + task.finish) / 2 - first),
                                y=(pos + 0.5) * (width + 2 * padding) + padding)
                background = rect.get("fill") or result["fill"]
                self.style.setattrs_text(label, background=background)
                if task.style:  # Use task styles, if given.
                    task.style.setattrs_text(label, background=background)
                label += task.label
                result += label
        return result

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        data = super().as_dict_content()
        data["width"] = self.width
        data["tasks"] = [t.as_dict() in self.tasks]
        return data


add_diagram(Gantt)


class Task:
    "Task to be part of a Gantt chart."

    def __init__(self, label, start, finish, style=None):
        self.label = str(label)
        if type(start) != type(finish):
            raise ValueError("task 'start' and 'finish' must be of same type")
        if isinstance(start, (int, float, datetime.date)):
            self.start = start
            self.finish = finish
        elif isinstance(start, str):
            self.start = datetime.date.fromisoformat(start)
            self.finish = datetime.date.fromisoformat(finish)
        else:
            raise ValueError("invalid task 'start' specification")
        if self.start > self.finish:
            raise ValueError("task 'start' must be less than 'finish'")
        self.style = style

    def as_dict(self):
        data = dict(label=self.label)
        if isinstance(self.start, datetime.date):
            data["start"] = self.start.isoformat()
            data["finish"] = self.finish.isoformat()
        else:
            data["start"] = self.start
            data["finish"] = self.finish
        return {"task": data}
