import pygame as pg
import random, time, sys
from pygame.locals import *
from consts import *
from tetris_logger import logger  


def pauseScreen():
    logger.info("Активирован экран паузы")
    pause = pg.Surface((600, 500), pg.SRCALPHA)
    pause.fill((0, 0, 255, 127))
    display_surf.blit(pause, (0, 0))


def main():
    global fps_clock, display_surf, basic_font, big_font

    logger.info("=" * 50)
    logger.info("ЗАПУСК ИГРЫ 'ТЕТРИС LITE'")
    logger.info(f"Размер окна: {window_w}x{window_h}, FPS: {fps}")
    logger.info("=" * 50)

    pg.init()
    fps_clock = pg.time.Clock()
    display_surf = pg.display.set_mode((window_w, window_h))
    basic_font = pg.font.SysFont('arial', 20)
    big_font = pg.font.SysFont('verdana', 45)
    pg.display.set_caption('Тетрис Lite')

    logger.debug("Инициализация PyGame завершена успешно")
    showText('Тетрис Lite')

    while True:
        logger.info("Начало новой игровой сессии")
        runTetris()
        pauseScreen()
        logger.warning("Игровая сессия завершена")
        showText('Игра закончена')


def runTetris():
    logger.debug("Создание игрового поля (стакана)")
    cup = emptycup()
    last_move_down = time.time()
    last_side_move = time.time()
    last_fall = time.time()
    going_down = False
    going_left = False
    going_right = False
    points = 0
    level, fall_speed = calcSpeed(points)

    logger.info(f"Начальные параметры: уровень={level}, скорость падения={fall_speed:.3f}")

    fallingFig = getNewFig()
    nextFig = getNewFig()

    logger.debug(f"Первая фигура: {fallingFig['shape']}, следующая: {nextFig['shape']}")

    while True:
        if fallingFig is None:
            fallingFig = nextFig
            nextFig = getNewFig()
            last_fall = time.time()

            logger.debug(f"Новая активная фигура: {fallingFig['shape']}, вращение: {fallingFig['rotation']}")
            logger.debug(f"Следующая фигура: {nextFig['shape']}")

            if not checkPos(cup, fallingFig):
                logger.critical("ИГРА ОКОНЧЕНА: Нет свободного места для новой фигуры!")
                logger.info(f"Финальный счет: {points}, достигнутый уровень: {level}")
                return

        quitGame()

        for event in pg.event.get():
            if event.type == KEYUP:
                if event.key == K_SPACE:
                    logger.info("Игра приостановлена пользователем")
                    pauseScreen()
                    showText('Пауза')
                    last_fall = time.time()
                    last_move_down = time.time()
                    last_side_move = time.time()
                elif event.key == K_LEFT:
                    going_left = False
                    logger.debug("Клавиша 'ВЛЕВО' отпущена")
                elif event.key == K_RIGHT:
                    going_right = False
                    logger.debug("Клавиша 'ВПРАВО' отпущена")
                elif event.key == K_DOWN:
                    going_down = False
                    logger.debug("Ускоренное падение отключено")

            elif event.type == KEYDOWN:
                if event.key == K_LEFT and checkPos(cup, fallingFig, adjX=-1):
                    fallingFig['x'] -= 1
                    going_left = True
                    going_right = False
                    last_side_move = time.time()
                    logger.debug(f"Движение влево: x={fallingFig['x']}")

                elif event.key == K_RIGHT and checkPos(cup, fallingFig, adjX=1):
                    fallingFig['x'] += 1
                    going_right = True
                    going_left = False
                    last_side_move = time.time()
                    logger.debug(f"Движение вправо: x={fallingFig['x']}")

                elif event.key == K_UP:
                    old_rotation = fallingFig['rotation']
                    fallingFig['rotation'] = (fallingFig['rotation'] + 1) % len(figures[fallingFig['shape']])
                    if not checkPos(cup, fallingFig):
                        fallingFig['rotation'] = (fallingFig['rotation'] - 1) % len(figures[fallingFig['shape']])
                        logger.debug(f"Поворот невозможен. Возврат к вращению {fallingFig['rotation']}")
                    else:
                        logger.debug(
                            f"Поворот фигуры {fallingFig['shape']}: {old_rotation} -> {fallingFig['rotation']}")

                elif event.key == K_DOWN:
                    going_down = True
                    if checkPos(cup, fallingFig, adjY=1):
                        fallingFig['y'] += 1
                    last_move_down = time.time()
                    logger.debug("Активировано ускоренное падение")

                elif event.key == K_RETURN:
                    logger.info("Мгновенный сброс фигуры вниз")
                    going_down = False
                    going_left = False
                    going_right = False
                    for i in range(1, cup_h):
                        if not checkPos(cup, fallingFig, adjY=i):
                            break
                    fallingFig['y'] += i - 1
                    logger.debug(f"Фигура сброшена на {i - 1} позиций, y={fallingFig['y']}")

        # Управление падением фигуры при удержании клавиш
        if (going_left or going_right) and time.time() - last_side_move > side_freq:
            if going_left and checkPos(cup, fallingFig, adjX=-1):
                fallingFig['x'] -= 1
                logger.debug(f"Автодвижение влево: x={fallingFig['x']}")
            elif going_right and checkPos(cup, fallingFig, adjX=1):
                fallingFig['x'] += 1
                logger.debug(f"Автодвижение вправо: x={fallingFig['x']}")
            last_side_move = time.time()

        if going_down and time.time() - last_move_down > down_freq and checkPos(cup, fallingFig, adjY=1):
            fallingFig['y'] += 1
            last_move_down = time.time()
            logger.debug(f"Ускоренное падение: y={fallingFig['y']}")

        if time.time() - last_fall > fall_speed:
            if not checkPos(cup, fallingFig, adjY=1):
                logger.info(
                    f"Фигура {fallingFig['shape']} приземлилась на позиции ({fallingFig['x']}, {fallingFig['y']})")
                addToCup(cup, fallingFig)
                lines_cleared = clearCompleted(cup)
                if lines_cleared > 0:
                    logger.info(f"Удалено {lines_cleared} линий! +{lines_cleared} очков")
                    points += lines_cleared
                level, fall_speed = calcSpeed(points)
                fallingFig = None
            else:
                fallingFig['y'] += 1
                last_fall = time.time()
                logger.debug(f"Автопадение фигуры: y={fallingFig['y']}")

        # Отрисовка
        display_surf.fill(bg_color)
        drawTitle()
        gamecup(cup)
        drawInfo(points, level)
        drawnextFig(nextFig)
        if fallingFig is not None:
            drawFig(fallingFig)
        pg.display.update()
        fps_clock.tick(fps)


def txtObjects(text, font, color):
    return font.render(text, True, color), font.render(text, True, color).get_rect()


def stopGame():
    logger.info("Завершение работы игры")
    pg.quit()
    sys.exit()


def checkKeys():
    quitGame()
    for event in pg.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showText(text):
    titleSurf, titleRect = txtObjects(text, big_font, title_color)
    titleRect.center = (int(window_w / 2) - 3, int(window_h / 2) - 3)
    display_surf.blit(titleSurf, titleRect)

    pressKeySurf, pressKeyRect = txtObjects('Нажмите любую клавишу для продолжения', basic_font, title_color)
    pressKeyRect.center = (int(window_w / 2), int(window_h / 2) + 100)
    display_surf.blit(pressKeySurf, pressKeyRect)

    logger.debug(f"Отображение текста: '{text}'")
    while checkKeys() is None:
        pg.display.update()
        fps_clock.tick()


def quitGame():
    for event in pg.event.get(QUIT):
        logger.info("Получено событие выхода из игры")
        stopGame()
    for event in pg.event.get(KEYUP):
        if event.key == K_ESCAPE:
            logger.info("Выход из игры по нажатию ESC")
            stopGame()
        pg.event.post(event)


def calcSpeed(points):
    level = min(11, int(points / 10) + 1)
    fall_speed = 0.27 - (level * 0.02)
    logger.info(f"Обновление уровня: {level}, скорость падения: {fall_speed:.3f}")
    return level, fall_speed


def getNewFig():
    shape = random.choice(list(figures.keys()))
    newFigure = {
        'shape': shape,
        'rotation': random.randint(0, len(figures[shape]) - 1),
        'x': int(cup_w / 2) - int(fig_w / 2),
        'y': -2,
        'color': random.randint(0, len(colors) - 1)
    }
    logger.debug(f"Сгенерирована новая фигура: {shape}, вращение: {newFigure['rotation']}, цвет: {newFigure['color']}")
    return newFigure


def addToCup(cup, fig):
    logger.debug(f"Добавление фигуры {fig['shape']} в стакан на позиции ({fig['x']}, {fig['y']})")
    for x in range(fig_w):
        for y in range(fig_h):
            if figures[fig['shape']][fig['rotation']][y][x] != empty:
                cup[x + fig['x']][y + fig['y']] = fig['color']


def emptycup():
    logger.debug("Создание пустого игрового поля")
    return [[empty] * cup_h for _ in range(cup_w)]


def incup(x, y):
    return 0 <= x < cup_w and y < cup_h


def checkPos(cup, fig, adjX=0, adjY=0):
    for x in range(fig_w):
        for y in range(fig_h):
            abovecup = y + fig['y'] + adjY < 0
            if abovecup or figures[fig['shape']][fig['rotation']][y][x] == empty:
                continue
            if not incup(x + fig['x'] + adjX, y + fig['y'] + adjY):
                logger.debug(f"Позиция вне границ: x={x + fig['x'] + adjX}, y={y + fig['y'] + adjY}")
                return False
            if cup[x + fig['x'] + adjX][y + fig['y'] + adjY] != empty:
                logger.debug(f"Коллизия с другой фигурой на позиции: ({x + fig['x'] + adjX}, {y + fig['y'] + adjY})")
                return False
    return True


def isCompleted(cup, y):
    for x in range(cup_w):
        if cup[x][y] == empty:
            return False
    return True


def clearCompleted(cup):
    removed_lines = 0
    y = cup_h - 1
    while y >= 0:
        if isCompleted(cup, y):
            logger.debug(f"Обнаружена заполненная линия: y={y}")
            for pushDownY in range(y, 0, -1):
                for x in range(cup_w):
                    cup[x][pushDownY] = cup[x][pushDownY - 1]
            for x in range(cup_w):
                cup[x][0] = empty
            removed_lines += 1
        else:
            y -= 1
    return removed_lines


def convertCoords(block_x, block_y):
    return (side_margin + (block_x * block)), (top_margin + (block_y * block))


def drawBlock(block_x, block_y, color, pixelx=None, pixely=None):
    if color == empty:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(block_x, block_y)
    pg.draw.rect(display_surf, colors[color], (pixelx + 1, pixely + 1, block - 1, block - 1), 0, 3)
    pg.draw.rect(display_surf, lightcolors[color], (pixelx + 1, pixely + 1, block - 4, block - 4), 0, 3)
    pg.draw.circle(display_surf, colors[color], (pixelx + block / 2, pixely + block / 2), 5)


def gamecup(cup):
    pg.draw.rect(display_surf, brd_color, (side_margin - 4, top_margin - 4, (cup_w * block) + 8, (cup_h * block) + 8),
                 5)
    pg.draw.rect(display_surf, bg_color, (side_margin, top_margin, block * cup_w, block * cup_h))
    for x in range(cup_w):
        for y in range(cup_h):
            drawBlock(x, y, cup[x][y])


def drawTitle():
    titleSurf = big_font.render('Тетрис Lite', True, title_color)
    titleRect = titleSurf.get_rect()
    titleRect.topleft = (window_w - 425, 30)
    display_surf.blit(titleSurf, titleRect)


def drawInfo(points, level):
    pointsSurf = basic_font.render(f'Баллы: {points}', True, txt_color)
    pointsRect = pointsSurf.get_rect()
    pointsRect.topleft = (window_w - 550, 180)
    display_surf.blit(pointsSurf, pointsRect)

    levelSurf = basic_font.render(f'Уровень: {level}', True, txt_color)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (window_w - 550, 250)
    display_surf.blit(levelSurf, levelRect)

    pausebSurf = basic_font.render('Пауза: пробел', True, info_color)
    pausebRect = pausebSurf.get_rect()
    pausebRect.topleft = (window_w - 550, 420)
    display_surf.blit(pausebSurf, pausebRect)

    escbSurf = basic_font.render('Выход: Esc', True, info_color)
    escbRect = escbSurf.get_rect()
    escbRect.topleft = (window_w - 550, 450)
    display_surf.blit(escbSurf, escbRect)


def drawFig(fig, pixelx=None, pixely=None):
    figToDraw = figures[fig['shape']][fig['rotation']]
    if pixelx is None and pixely is None:
        pixelx, pixely = convertCoords(fig['x'], fig['y'])

    for x in range(fig_w):
        for y in range(fig_h):
            if figToDraw[y][x] != empty:
                drawBlock(None, None, fig['color'], pixelx + (x * block), pixely + (y * block))


def drawnextFig(fig):
    nextSurf = basic_font.render('Следующая:', True, txt_color)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (window_w - 150, 180)
    display_surf.blit(nextSurf, nextRect)
    drawFig(fig, pixelx=window_w - 150, pixely=230)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception(f"КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
        raise
