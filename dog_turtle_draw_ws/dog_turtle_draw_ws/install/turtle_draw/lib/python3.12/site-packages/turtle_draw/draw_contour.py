import os
import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen
import numpy as np
from ament_index_python.packages import get_package_share_directory


# Distância máxima entre pontos consecutivos para manter a caneta abaixada.
# Saltos maiores que esse valor indicam transição entre contornos distintos.
PEN_UP_THRESHOLD = 0.8


class DrawContourNode(Node):

    def __init__(self):
        super().__init__('draw_contour')

        pkg_share = get_package_share_directory('turtle_draw')
        points_path = os.path.join(pkg_share, 'data', 'turtle_points.npy')
        self.points = np.load(points_path)
        self.get_logger().info(f'Carregados {len(self.points)} pontos do contorno.')

        self.teleport_client = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute'
        )
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        self.get_logger().info('Aguardando serviços do turtlesim...')
        self.teleport_client.wait_for_service()
        self.pen_client.wait_for_service()
        self.get_logger().info('Serviços prontos. Iniciando desenho.')

    def _set_pen(self, r: int, g: int, b: int, width: int, off: bool):
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = width
        req.off = int(off)
        future = self.pen_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def _teleport(self, x: float, y: float):
        req = TeleportAbsolute.Request()
        req.x = float(x)
        req.y = float(y)
        req.theta = 0.0
        future = self.teleport_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def draw(self):
        points = self.points
        total = len(points)

        # Move para o primeiro ponto com caneta levantada
        self._set_pen(0, 0, 0, 1, True)
        self._teleport(points[0][0], points[0][1])
        self._set_pen(255, 255, 255, 2, False)

        for i in range(1, total):
            px, py = points[i]
            prev_x, prev_y = points[i - 1]

            dist = float(np.hypot(px - prev_x, py - prev_y))

            if dist > PEN_UP_THRESHOLD:
                # Salto entre contornos: levanta caneta, teleporta, desce
                self._set_pen(0, 0, 0, 1, True)
                self._teleport(px, py)
                self._set_pen(255, 255, 255, 2, False)
            else:
                self._teleport(px, py)

            if i % 100 == 0:
                self.get_logger().info(f'Progresso: {i}/{total} pontos')

        self.get_logger().info('Desenho concluído!')


def main(args=None):
    rclpy.init(args=args)
    node = DrawContourNode()
    try:
        node.draw()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
