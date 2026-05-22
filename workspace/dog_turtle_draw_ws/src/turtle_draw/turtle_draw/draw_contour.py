import os
import rclpy
from rclpy.node import Node
from turtlesim.srv import TeleportAbsolute, SetPen
import numpy as np
from ament_index_python.packages import get_package_share_directory


# Limiar de distância (em unidades do turtlesim) para detectar saltos entre
# contornos distintos. A imagem original tem vários contornos separados e os
# pontos de cada um chegam em sequência, então uma distância grande entre dois
# pontos consecutivos indica que foi mudado de contorno e a caneta deve ser levantada.
PEN_UP_THRESHOLD = 0.8


class DrawContourNode(Node):

    def __init__(self):
        super().__init__('draw_contour')

        # get_package_share_directory localiza a pasta share do pacote no
        # diretório de instalação do colcon, onde o setup.py copiou o .npy
        pkg_share = get_package_share_directory('turtle_draw')
        points_path = os.path.join(pkg_share, 'data', 'turtle_points.npy')
        self.points = np.load(points_path)
        self.get_logger().info(f'Carregados {len(self.points)} pontos do contorno.')

        # TeleportAbsolute posiciona a tartaruga diretamente em (x, y) sem
        # simular trajetória, o que é ideal para desenho ponto a ponto
        self.teleport_client = self.create_client(
            TeleportAbsolute, '/turtle1/teleport_absolute'
        )
        # SetPen controla cor RGB, espessura e estado da caneta (ligada/desligada)
        self.pen_client = self.create_client(SetPen, '/turtle1/set_pen')

        # Bloqueia a inicialização até o turtlesim estar no ar e os serviços
        # registrados no DDS, garantindo que já pode fazer chamadas
        self.get_logger().info('Aguardando serviços do turtlesim...')
        self.teleport_client.wait_for_service()
        self.pen_client.wait_for_service()
        self.get_logger().info('Serviços prontos. Iniciando desenho.')

    def _set_pen(self, r: int, g: int, b: int, width: int, off: bool):
        # call_async envia a requisição de forma não bloqueante e
        # spin_until_future_complete processa os callbacks até a resposta chegar
        req = SetPen.Request()
        req.r = r
        req.g = g
        req.b = b
        req.width = width
        req.off = int(off)
        future = self.pen_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def _teleport(self, x: float, y: float):
        # theta=0.0 mantém a tartaruga sempre na mesma orientação,
        # o que não afeta o desenho pois foi usado teleporte e não velocidade
        req = TeleportAbsolute.Request()
        req.x = float(x)
        req.y = float(y)
        req.theta = 0.0
        future = self.teleport_client.call_async(req)
        rclpy.spin_until_future_complete(self, future)

    def draw(self):
        points = self.points
        total = len(points)

        # Levanta a caneta e vai ao ponto inicial sem deixar rastro,
        # evitando uma linha da posição padrão da tartaruga até o contorno
        self._set_pen(0, 0, 0, 1, True)
        self._teleport(points[0][0], points[0][1])
        self._set_pen(255, 255, 255, 2, False)

        for i in range(1, total):
            px, py = points[i]
            prev_x, prev_y = points[i - 1]

            # Distância euclidiana entre o ponto atual e o anterior.
            # Saltos grandes indicam início de um contorno diferente na imagem.
            dist = float(np.hypot(px - prev_x, py - prev_y))

            if dist > PEN_UP_THRESHOLD:
                # Transição entre contornos: levanta a caneta antes de mover
                # para não conectar partes que são separadas no desenho original
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
