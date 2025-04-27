"Gantt chart."

__all__ = ["Gantt", "Task"]


from diagram import *
import utils


class Gantt(Diagram):
    "Gantt chart."

    DEFAULT_WIDTH = 500

    def __init__(
        self,
        id=None,
        klass=None,
        style=None,
        width=None,
        tasks=None,
    ):
        assert width is None or isinstance(width, (int, float))
        assert tasks is None or isinstance(tasks, (tuple, list))

        super().__init__(id=id, klass=klass, style=style)

        self.width = width if width is not None else self.DEFAULT_WIDTH
        self.tasks = []
        if tasks:
            for task in tasks:
                self.append(task)

    def __iadd__(self, other):
        self.append(other)
        return self

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
        self.tasks.append(item)

    def viewbox(self):
        height = 0
        padding = self.style["padding"] or 0
        lanes = set()
        for task in self.tasks:
            if task.lane in lanes:
                continue
            height += task.height + 2 * padding
            lanes.add(task.lane)
        return (Vector2(0, 0), Vector2(self.width, height))

    def svg(self):
        "Return the SVG minixml element for the diagram content."
        result = super().svg()

        offset = 0
        height = 0
        padding = self.style["padding"] or 0
        lanes = dict()
        for task in self.tasks:
            if task.lane:
                offset = max(offset, utils.get_text_length(task.lane, 14, "sans"))
            if task.lane in lanes:
                continue
            height += padding
            lanes[task.lane] = height
            height += task.height + padding

        lowest = None
        highest = None
        for task in self.tasks:
            lowest = task.lowest(lowest)
            highest = task.highest(highest)

        scaling = (self.width - offset) / (highest - lowest)
        xticks = [
            offset + scaling * (tick - lowest)
            for tick in utils.get_ticks(lowest, highest)
        ]
        path = Path(Vector2(xticks[0], 0)).V(height)
        for xtick in xticks[1:]:
            path.M(Vector2(xtick, 0)).V(height)
        result += Element("path", d=path)
        labels = Element("g")
        self.style.set_text_attributes(labels, "label", diff=False)
        legends = Element("g")
        self.style.set_text_attributes(legends, "legend", diff=False)

        for task in self.tasks:
            rect = Element(
                "rect",
                x=N(offset + scaling * (task.start - lowest)),
                y=N(lanes[task.lane]),
                width=N(scaling * (task.finish - task.start)),
                height=N(task.height),
                rx=self.style["rounded"],
                ry=self.style["rounded"],
            )
            if task.style:
                task.style.set_attribute(rect, "stroke")
                task.style.set_attribute(rect, "stroke-width")
                task.style.set_attribute(rect, "fill")
            result += rect

            if task.label:
                label = Element(
                    "text",
                    x=N(offset + scaling * ((task.start + task.finish) / 2 - lowest)),
                    y=N(lanes[task.lane] + task.height - self.style["padding"]),
                )
                if task.style:  # Task styles override, if given.
                    task.style.set_text_attributes(label, "label", diff=self.style)
                label += task.label
                labels.append(label)

            if task.lane:
                legend = Element(
                    "text",
                    x=0,
                    y=N(lanes[task.lane] + task.height - self.style["padding"]),
                )
                self.style.set_text_attributes(legend, "legend", diff=self.style)
                legend += task.lane
                legends.append(legend)

        # Labels and legends overwrite anything drawn prior.
        if len(labels):
            result += labels
        if len(legends):
            result += legends
        return result

    def as_dict_content(self):
        "Return content as a dictionary of basic YAML values."
        data = super().as_dict_content()
        data["tasks"] = [task.as_dict() for task in self.tasks]
        return data


add_diagram(Gantt)


class Task:
    "Task in a Gantt chart."

    DEFAULT_HEIGHT = 16

    def __init__(self, label, start, finish, height=None, lane=None, style=None):
        assert label and isinstance(label, str)
        assert isinstance(start, (int, float, str))
        assert type(start) == type(finish)
        assert height is None or isinstance(height, (int, float))
        assert lane is None or isinstance(lane, str)
        assert style is None or isinstance(style, (dict, Style))

        self.label = label
        if isinstance(start, (int, float)):
            self.start = start
            self.finish = finish
        assert self.start <= self.finish
        self.height = height if height is not None else self.DEFAULT_HEIGHT
        self.lane = lane if lane is not None else self.label
        if isinstance(style, dict):
            style = Style(**style)
        self.style = style

    def lowest(self, lowest=None):
        if lowest is None:
            return min(self.start, self.finish)
        else:
            return min(self.start, self.finish, lowest)

    def highest(self, highest=None):
        if highest is None:
            return max(self.start, self.finish)
        else:
            return max(self.start, self.finish, highest)

    def as_dict(self):
        data = dict(label=self.label)
        data["start"] = self.start
        data["finish"] = self.finish
        data["height"] = self.height
        return {"task": data}
