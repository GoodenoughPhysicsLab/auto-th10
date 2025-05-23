import os
import argparse
import cv2
import numpy as np
from . import window
from . import scene
from . import kb_control
from . import score
from typing import Optional

def main() -> None:
    parser = argparse.ArgumentParser(description="auto-th10: play th10 automatically")

    parser.add_argument("--version", action="store_true", help="show version")
    parser.add_argument("--always-shoot", action="store_true", help="player always shoot without pressing 'z'")
    parser.add_argument("--draw", action="store_true", help="draw the scene")

    args = parser.parse_args()

    if args.version:
        print("thtool(TouHouTool) v0.0.0")
        return

    if args.bind == "list":
        window.print_all_windows()
        return
    elif args.bind == "list-guessed":
        window.print_all_windows(only_guess=True)
        return
    elif args.bind == "foreground":
        window.bind_foreground()
    elif args.bind:
        window.bind_title(args.bind)
    else:
        window.bind_auto()

    if args.always_shoot:
        kb_control.send(kb_control.Behavior.shoot, deltatime=None, in_queue=True)

    game_start_status: Optional[bool] = None # False: not start, True: start, None: not checked
    window.init_Gdiplus()
    try:
        while True:
            kb_control.do_if_checkout_foreground()

            try:
                img = scene.get_scene() # raise BindError if th-window closed
                player_point = scene.get_player_point() # raise GameNotStartError if game not start
                enemy_points = scene.get_enemy_points()
                enemy_bullet_points = scene.get_enemy_bullet_points()
                enemy_laser_points = scene.get_enemy_laser_points()
                resource_points = scene.get_resource_points()
            except window.GameNotStartError:
                cv2.destroyAllWindows()
                if game_start_status is not False:
                    print("Checking touhou game NOT start")
                    game_start_status = False
            else:
                if game_start_status is not True:
                    print("Checking touhou game start")
                    game_start_status = True

                if args.draw:
                    blank = img.copy() # debug
                    # blank = np.zeros_like(img)

                    # draw player
                    cv2.rectangle(blank, *player_point, (255, 0, 0))

                    #draw enemies
                    for enemy_point in enemy_points:
                        cv2.rectangle(blank, *enemy_point, (0, 0, 255))

                    # draw enemy_bullets
                    for enemy_bullet_point in enemy_bullet_points:
                        cv2.rectangle(blank, *enemy_bullet_point, (0, 0, 255))

                    # draw enemy_lasers
                    for enemy_laser_point in enemy_laser_points:
                        pts = np.array(enemy_laser_point, dtype=np.int32)
                        cv2.polylines(blank, [pts], True, (0, 0, 255))

                    # draw resources
                    for resource_point in resource_points:
                        cv2.rectangle(blank, *resource_point, (0, 255, 0))

                    cv2.imshow("thtool", blank)
                    cv2.waitKey(1)
    except window.BindError:
        print("Checking touhou window closed")
        exit(0)
    finally:
        kb_control.release_all()
        cv2.destroyAllWindows()
        window.free_Gdiplus()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard interrupted!")
else:
    raise RuntimeError("This file is not intended to be imported!")
