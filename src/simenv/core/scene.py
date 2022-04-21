class Scene:
    def __init__(self, start_frame=0, end_frame=500, frame_rate=24):
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.frame_rate = frame_rate
        self.nodes = []
        self.views = []

    def add(self, node):
        self.nodes.append(node)
        for view in self.views:
            view.add(node)

    def __iadd__(self, node):
        self.add(node)
        return self

    def remove(self, node):
        self.nodes.remove(node)
        for view in self.views:
            view.remove(node)

    def link_view(self, view):
        if view not in self.views:
            self.views.append(view)
        for node in self.nodes:
            view.add(node)

    def unlink_view(self, view):
        if view in self.views:
            self.views.remove(view)
        for node in self.nodes:
            view.remove(node)
