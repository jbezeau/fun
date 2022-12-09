import pygame
import random
import enemy
import player
import environment as env
import static as s


def draw_status_text(status, colour=(0, 32, 0)):
    size = min(512, 2600 // len(status))
    font = pygame.font.Font(None, size)
    text_output = font.render(status, True, colour)
    text_rect = text_output.get_rect(centerx=s.screen.get_width() // 2, centery=s.screen.get_height()//2)
    s.screen.blit(text_output, text_rect)


def draw_ship_text(ship, colour=(32, 32, 32)):
    size = 128
    font = pygame.font.Font(None, size)
    text_output = font.render('FIGHTER ' + ship, True, colour)
    text_rect = text_output.get_rect(centerx=s.screen.get_width() // 2, centery=s.screen.get_height()*3/4)
    s.screen.blit(text_output, text_rect)


def draw_score_text(points, colour=(32, 32, 32)):
    size = 128
    font = pygame.font.Font(None, size)
    text_output = font.render('SCORE ' + str(points), True, colour)
    text_rect = text_output.get_rect(centerx=s.screen.get_width() // 2, centery=s.screen.get_height()//4)
    s.screen.blit(text_output, text_rect)


if __name__ == '__main__':
    clock = pygame.time.Clock()
    pygame.display.set_caption('Shooter: I can work it out')

    new_game = True
    while new_game:
        start = (s.screen.get_width()//3, s.screen.get_height()//2)
        score = 0
        p1 = player.build_ship(start)

        env.parallax.empty()
        env.objects.empty()
        enemy.objects.empty()
        enemy.bullets.empty()

        # orientation just controls if obstacles are generated on top or bottom of the environment
        orientation = True
        playing = True
        active = False
        timer = 0
        while playing:
            clock.tick(60)
            s.screen.fill(s.SPACE)

            if active and p1.alive():
                score += len(player.ship) + len(enemy.objects) + len(enemy.bullets)

                env.objects.update()
                env.parallax.update()
                pygame.sprite.groupcollide(enemy.objects, env.objects, True, False)
                pygame.sprite.groupcollide(enemy.bullets, env.objects, True, False)
                pygame.sprite.groupcollide(player.bullets, env.objects, True, False)
                pygame.sprite.groupcollide(player.ship, env.objects, True, False)

                player.ship.update()
                player.bullets.update()
                pygame.sprite.groupcollide(enemy.objects, player.bullets, True, True)

                enemy.objects.update()
                enemy.bullets.update()
                pygame.sprite.groupcollide(player.ship, enemy.objects, True, True)
                pygame.sprite.groupcollide(player.ship, enemy.bullets, True, True)

                draw_status_text(str(score), (16, 16, 16))

                env.parallax.draw(s.screen)
                player.bullets.draw(s.screen)
                player.ship.draw(s.screen)
                enemy.bullets.draw(s.screen)
                enemy.objects.draw(s.screen)
                env.objects.draw(s.screen)

                timer += 1
                if timer % 20 == 0:
                    # add enemy to the list
                    enemy.new_enemy((s.screen.get_width()-16, random.randrange(s.screen.get_height())))
                # add obstacle to the list
                orientation = env.new_obstacle(orientation, 2)

            else:
                if timer == 0:
                    draw_status_text('START')
                elif not p1.alive():
                    draw_ship_text(p1.name)
                    draw_status_text('GAME OVER', (64, 0, 0))
                    draw_score_text(score)
                elif not active:
                    draw_ship_text(p1.name)
                    draw_status_text('PAUSE')
                    draw_score_text(score)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    playing = False
                    new_game = False
                if event.type == pygame.KEYDOWN:
                    if p1.alive():
                        active = not active
                    else:
                        playing = False

            # suppress mouse when playing
            if active and p1.alive():
                pygame.mouse.set_visible(False)
            else:
                pygame.mouse.set_visible(True)

    pygame.quit()
