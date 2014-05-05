#!/usr/bin/env python
class graph:
  def __init__(self, directional = False):
    self.directional = directional
    self.edges = {}
    self.nodes = []

  def _addEdge(self, source, destination):
    if self.edges.has_key(source):
      self.edges[source] |= set([destination])
    else:
      self.edges[source] = set([destination])

  def addEdge(self, source, destination):
    self._addEdge(source, destination)
    if self.directional:
      self._addEdge(destination, source)

  def _isEmpty(self, s):
    if len(s) == 0: return True
    return False

  def isConnected(self, nodeOne, nodeTwo):
    if self.edges.has_key(nodeOne):
      if not self._isEmpty(self.edges[nodeOne] & set([nodeTwo])):
        return True

    return False
