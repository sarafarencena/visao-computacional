# Robótica e Visão Computacional

Pipeline de visão computacional e pacote ROS 2 para o turtlesim desenhar o contorno de uma imagem.

## Estrutura do projeto

```text
dog_turtle_draw_ws/
├── pond_visao_computacional(5_1).ipynb   # pipeline de visão computacional
├── src/
│   └── turtle_draw/
│       ├── data/
│       │   └── turtle_points.npy         # pontos do contorno gerados pelo notebook
│       ├── turtle_draw/
│       │   └── draw_contour.py           # nó ROS 2 que controla a tartaruga
│       ├── package.xml
│       └── setup.py
```

## Ambiente de desenvolvimento

### Dependências

| Dependência | Versão | Uso no projeto |
|---|---|---|
| Ubuntu | 24.04 | Sistema operacional base |
| ROS 2 Jazzy | Jazzy | Framework robótico (comunicação entre nós e serviços do turtlesim) |
| Python | 3.10+ | Linguagem principal do projeto |
| NumPy | 2.0+ | Todas as operações matriciais da pipeline de visão computacional |
| Matplotlib | 3.10+ | Visualização das imagens e dos pontos ao longo do processamento |
| OpenCV | 4.13+ | Exclusivamente para carregamento da imagem via `cv2.imread` |
| turtlesim | — | Simulador 2D do ROS 2 onde o contorno é desenhado |


## Build do pacote

```bash
cd ~/dog_turtle_draw_ws
source /opt/ros/jazzy/setup.bash
colcon build --packages-select turtle_draw
```

## Execução

### Terminal 1 — iniciar o simulador

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

Aguarde a janela do turtlesim abrir completamente antes de prosseguir.

### Terminal 2 — executar o desenho

```bash
source ~/dog_turtle_draw_ws/install/setup.bash
ros2 run turtle_draw draw_contour
```

A tartaruga percorre os ~2000 pontos do contorno automaticamente,
levantando a caneta ao transitar entre regiões separadas do desenho.


## Gerando os pontos do contorno (opcional)

Os pontos já estão pré-gerados em:

```text
src/turtle_draw/data/turtle_points.npy
```

Para regenerá-los a partir da imagem original, execute o notebook:

```bash
jupyter notebook "pond_visao_computacional(5_1).ipynb"
```

Execute todas as células em ordem. O arquivo `turtle_points.npy`
será gerado no diretório atual. Copie-o para
`src/turtle_draw/data/` antes de fazer o build.


## Documentação técnica

> Acesse [aqui](https://github.com/sarafarencena/visao-computacional/blob/main/document/document.md) a documentação técnica detalhada do projeto.

---

## Vídeo demonstrativo

> [Inserir hyperlink]
