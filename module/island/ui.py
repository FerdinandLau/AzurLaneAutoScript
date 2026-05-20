import cv2
import numpy as np

from module.base.button import ButtonGrid
from module.base.decorator import cached_property
from module.base.utils import color_similarity_2d, rgb2luma
from module.combat.assets import GET_ITEMS_1
from module.island.assets import *
from module.ui.navbar import Navbar
from module.ui.scroll import Scroll
from module.ui.ui import UI


ISLAND_SEASON_TASK_SCROLL = Scroll(
    ISLAND_SEASON_TASK_SCROLL_AREA.button,
    color=(128, 128, 128),
    name="ISLAND_SEASON_TASK_SCROLL"
)


class IslandUI(UI):
    def ui_additional(self, get_ship=True):
        return super().ui_additional(get_ship=False)

    def has_white_band(self, threshold=1000):
        min_y = 405
        max_y = 560
        image = self.image_crop((0, min_y, 1280, max_y), copy=False)
        luma = rgb2luma(image)
        white_mask = cv2.inRange(luma, 200, 255)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (31, 3))
        white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
        row_white_width = (white_mask > 0).sum(axis=1)
        candidate_rows = row_white_width > threshold
        min_continuous_height = 50
        count = 0
        for ok in candidate_rows:
            if ok:
                count += 1
                if count >= min_continuous_height:
                    return True
            else:
                count = 0
        return False

    def handle_island_get_items(self):
        # if self.appear(ISLAND_GET_ITEMS, offset=(20, 20), interval=3):
        #     self.device.click(ISLAND_CLICK_SAFE_AREA)
        #     return True
        if self.appear(GET_ITEMS_1, offset=(20, 20), interval=3):
            self.device.click(ISLAND_CLICK_SAFE_AREA)
            return True
        if self.has_white_band():
            self.device.click(ISLAND_CLICK_SAFE_AREA)
            return True
        return False

    def handle_island_level_up(self):
        if self.appear(ISLAND_LEVEL_UP, offset=(20, 20), interval=3):
            self.device.click(ISLAND_CLICK_SAFE_AREA)
            return True
        return False

    def handle_island_additional(self):
        if self.handle_island_get_items():
            return True
        if self.handle_island_level_up():
            return True
        return False

    def is_button_selected(self, button, color=(57, 189, 255), threshold=221, count=100):
        """
        Detects if the button is surrounded by a blue border,
        which indicates that the button is chosen.

        Args:
            button (Button, tuple): Button instance or area.

        Returns:
            bool: True if the button is chosen, False otherwise.
        """
        if isinstance(button, np.ndarray):
            image = button
        else:
            image = self.image_crop(button, copy=False)
        mask = color_similarity_2d(image, color)
        cv2.inRange(mask, threshold, 255, dst=mask)
        mask[2:-2, 2:-2] = 0
        sum_ = cv2.countNonZero(mask)
        return sum_ > count

    @cached_property
    def _island_season_bottom_navbar(self):
        """
        6 options:
            homepage,
            pt_reward,
            season_task,
            season_shop,
            season_rank,
            season_history
        """
        island_season_bottom_navbar = ButtonGrid(
            origin=(14, 677), delta=(213, 0),
            button_shape=(186, 33), grid_shape=(6, 1),
            name='ISLAND_SEASON_BOTTOM_NAVBAR'
        )
        return Navbar(grids=island_season_bottom_navbar,
                      active_color=(237, 237, 237),
                      inactive_color=(65, 78, 96),
                      active_count=500,
                      inactive_count=500)

    def island_season_bottom_navbar_ensure(self, left=None, right=None):
        """
        Args:
            left (int):
                1 for homepage,
                2 for pt_reward,
                3 for season_task,
                4 for season_shop,
                5 for season_rank,
                6 for season_history
            right (int):
                1 for season_history,
                2 for season_rank,
                3 for season_shop,
                4 for season_task,
                5 for pt_reward,
                6 for homepage

        """
        if self._island_season_bottom_navbar.set(self, left=left, right=right):
            return True
        return False

    @cached_property
    def _island_technology_side_navbar(self):
        island_technology_side_navbar = ButtonGrid(
            origin=(13, 107), delta=(0, 196/3),
            button_shape=(128, 43), grid_shape=(1, 5)
        )
        return Navbar(grids=island_technology_side_navbar,
                      active_color=(30, 143, 255),
                      inactive_color=(50, 52, 55),
                      active_count=500,
                      inactive_count=500)

    def _island_technology_side_navbar_get_active(self):
        active, _, _ = self._island_technology_side_navbar.get_info(main=self)
        if active is None:
            return 1
        return active + 2

    def island_technology_side_navbar_ensure(self, tab=1, skip_first_screenshot=True):
        """
        Tab 2, 3, 4, 5, 6 corresponds to _island_technology_side_navbar 1, 2, 3, 4, 5
        Tab 1 is a special situation where the botton icon is chosen,
        and all the navbar icons are inactive.
        """
        for _ in self.loop(skip_first=skip_first_screenshot):
            active = self._island_technology_side_navbar_get_active()
            if active == tab:
                return True
            if tab == 1:
                self.device.click(ISLAND_TECHNOLOGY_TAB1)
                continue
            else:
                if active == 1:
                    self.device.click(self._island_technology_side_navbar.grids.buttons[tab-2])
                    continue
                else:
                    self._island_technology_side_navbar.set(self, upper=tab-1)
                    return True
        return False

    @cached_property
    def _island_manage_side_navbar(self):
        island_manage_side_navbar = ButtonGrid(
            origin=(13, 107), delta=(0, 196/3),
            button_shape=(128, 43), grid_shape=(1, 3)
        )
        return Navbar(grids=island_manage_side_navbar,
                      active_color=(57, 189, 255),
                      inactive_color=(50, 52, 55),
                      active_count=500,
                      inactive_count=500)

    def island_manage_side_navbar_ensure(self, upper=1, skip_first_screenshot=True):
        """
        Args: 
            upper (int):
                1 for production,
                2 for restaurant,
                3 for collect
            bottom (int):
                1 for collect,
                2 for restaurant,
                3 for production
        """
        return self._island_manage_side_navbar.set(self, upper=upper, skip_first_screenshot=skip_first_screenshot)