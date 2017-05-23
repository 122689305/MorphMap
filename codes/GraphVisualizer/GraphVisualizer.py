#!/usr/bin/env python3

# This file is to convert Element Graph to Visualization Graph. It will read the primal graph.

import sys
sys.path.insert(0, '../../')
from codes.Element import Element
import graph_tool.all as gt

class GraphVisualizer():
  
  def __init__(self):
    self.vg = gt.Graph()
    self.vg.vp.name = self.vg.new_vertex_property('string')
    self.vg.ep.name = self.vg.new_edge_property('string')
    self.eg_vg_dict = {}

  #function: convertElementGraph2VisualizationGraph 
  def convertEG2VG(self, element_list):
    vg = self.vg
    for ent in element_list:
      if ent.element_type == Element.ElementType.entity:
        v = vg.add_vertex()
        vg.vp.name[v] = ent.name
        self.eg_vg_dict[ent] = v
    for ent in element_list:
      if ent.element_type == Element.ElementType.relation:
        #print(ent.name, ent.parent.name)
        v_parent = self.eg_vg_dict[ent.parent]
        v_child = self.eg_vg_dict[ent.children[0]]
        e = vg.add_edge(v_parent, v_child)
        vg.ep.name[e] = ent.name
    return vg        
    
  def show(self):
    vg = self.vg
    gt.graph_draw(vg, vertex_text=vg.vp.name, edge_text=vg.ep.name, vertex_font_size=6)

  def getElementList(self, root_element):
    root = root_element
    def _get(node, element_list):
      if node:
        element_list.append(node)
        for e in node.children:
          if e.level > node.level:
            _get(e, element_list)
    element_list = []
    _get(root, element_list)
    return element_list

def test1():
  from codes.GraphBuilder.GraphBuilder import GraphBuilder
  gb = GraphBuilder('李自成')
  gb.getGraph()
  gv = GraphVisualizer()
  eleList = gv.getElementList(gb.root)
  '''
  for e in eleList:
    if e.name:
      print(id(e), e.name, e.level)
      for se in e.children:
        print(id(se.parent), se.parent.name, se.name)
  '''
  vg = gv.convertEG2VG(eleList)
  gv.show()

if __name__ == '__main__':
  test1()
