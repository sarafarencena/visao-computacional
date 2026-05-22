import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/matheus/dog_turtle_draw_ws/install/turtle_draw'
