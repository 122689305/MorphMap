#!/usr/bin/env python3

# This file is to convert Element Graph to Visualization Graph. It will read the primal graph.

import sys
sys.path.insert(0, '../../')
from codes.Element import Element
import graph_tool.all as gt
import os

class GraphVisualizer():
  
  #function: convertElementGraph2VisualizationGraph 
  def convertEG2VG(self, element_list):
    vg = gt.Graph()
    vg.vp.name = vg.new_vertex_property('object')
    vg.ep.name = vg.new_edge_property('object')
    eg_vg_dict = {}
    for ent in element_list:
      if ent.element_type == Element.ElementType.entity:
        v = vg.add_vertex()
        vg.vp.name[v] = (ent.parent.name[:10] +':' if ent.parent else '') +ent.name[:10]
        eg_vg_dict[ent] = v
    for ent in element_list:
      if ent.element_type == Element.ElementType.relation:
        #print(ent.name, ent.parent.name)
        v_parent = eg_vg_dict[ent.parent]
        for ec in ent.children:
          v_child = eg_vg_dict[ec]
          e = vg.add_edge(v_parent, v_child)
        vg.ep.name[e] = ent.name[:10]
    return vg        
   
  def getImage(self, vg, output_image='vg.png'):
    #mpl.rcParams['font.family'] = ['Noto Sans CJK SC Thin']
    gt.graph_draw(vg, bg_color=[1.,1.,1.,1], vertex_text_position=-0.5, vertex_text=vg.vp.name,vertex_text_color=[0.,0.,0.,1], edge_text=vg.ep.name, vertex_font_size=15, edge_font_size=1, edge_pen_width=1, edge_text_distance=0.9, vertex_size=80, vertex_font_family='Noto Sans CJK SC Thin', edge_font_family='Noto Sans CJK SC Thin', output=output_image, output_size=(6000,6000))
    

  def show(self, vg, output_image='vg.png'):
    self.getImage(vg, output_image)
    import subprocess
    subprocess.call(['xdg-open',output_image])

  def getElementList(self, root_element):
    root = root_element
    def _get(node, element_list):
      if node:
        element_list.append(node)
        for e in node.children:
          if e.parent == node and e.level >= node.level and (not e.name == 'subEntity' or len(e.children[0].children) < 20):
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
  gv.show(vg, 'test1_李自成.svg')

def test2():
  from codes.GraphBuilder.GraphBuilder import GraphBuilder
  gb = GraphBuilder('薄熙来')
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
  gv.show(vg, 'test2_薄熙来.svg')

def test3():
  entity_morph = [('薄熙来', '平西王'), ('毛泽东', '太祖'), ('陈光诚', '盲人'), ('王立军','西南王警官'),('德文·韦德', '闪电侠'), ('金正恩', '金胖子'), ('蒋介石', '常公公'), ('杨幂','函数')]
  output_dir = os.path.dirname(__file__)
  gv = GraphVisualizer()
  from codes.GraphBuilder.GraphBuilder import GraphBuilder
  for em in entity_morph:
    for x in em:
      gb = GraphBuilder(x)
      gb.getGraph()
      eleList = gv.getElementList(gb.root)
      vg = gv.convertEG2VG(eleList)
      gv.getImage(vg, os.path.join(output_dir, gb.root.name +'.svg'))

def test4():
  entity_morph = [('薄熙来', '平西王'), ('毛泽东', '太祖'), ('陈光诚', '盲人'), ('王立军','西南王警官'),('德文·韦德', '闪电侠'), ('金正恩', '金胖子'), ('蒋介石', '常公公'), ('杨幂','函数')]
  output_dir = os.path.dirname(__file__)
  gv = GraphVisualizer()
  from codes.GraphBuilder.GraphBuilder import GraphBuilder
  for em in entity_morph:
    eleList = []
    names = []
    for x in em:
      gb = GraphBuilder(x)
      gb.getGraph()
      eleList += gv.getElementList(gb.root)
      names += [gb.root.name]
    eleList = list(set(eleList))
    vg = gv.convertEG2VG(eleList)
    gv.getImage(vg, os.path.join(output_dir, '_'.join(names) +'.svg'))


if __name__ == '__main__':
  test4()
  #test2()
