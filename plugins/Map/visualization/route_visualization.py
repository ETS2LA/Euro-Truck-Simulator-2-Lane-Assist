from typing import List, Optional
import pygame
from ..classes import Node, Position
from ..navigation.classes import NavigationLane
from ..utils.math_helpers import DistanceBetweenPoints
import logging

class RouteVisualizer:
    def __init__(self, screen_width: int = 800, screen_height: int = 600):
        self.screen_width = screen_width
        self.screen_height = screen_height
        try:
            pygame.init()
            self.screen = pygame.display.set_mode((screen_width, screen_height))
            self.scale = 1.0
            self.offset_x = 0
            self.offset_y = 0
        except Exception as e:
            logging.error(f"Failed to initialize pygame: {e}")
            raise

    def _world_to_screen(self, x: float, z: float) -> tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        screen_x = int((x + self.offset_x) * self.scale + self.screen_width / 2)
        screen_y = int((z + self.offset_y) * self.scale + self.screen_height / 2)
        return screen_x, screen_y

    def draw_route(self, route: List[Node], mode: str = 'shortest', color: tuple[int, int, int] = (0, 255, 0), show_stats: bool = True):
        """Draw a route on the screen with optional statistics."""
        if not route:
            return

        # Clear screen
        self.screen.fill((0, 0, 0))

        # Define colors for different road types
        HIGHWAY_COLOR = (255, 165, 0)  # Orange for highways
        RURAL_COLOR = (0, 255, 0)      # Green for rural roads
        PREFAB_COLOR = (0, 191, 255)   # Deep sky blue for prefabs

        # Draw nodes and connections
        total_distance = 0
        try:
            for i in range(len(route) - 1):
                start = route[i]
                end = route[i + 1]

                start_pos = self._world_to_screen(start.x, start.z)
                end_pos = self._world_to_screen(end.x, end.z)

                # Calculate segment distance
                segment_distance = DistanceBetweenPoints((start.x, start.z), (end.x, end.z))
                total_distance += segment_distance

                # Determine road type and color
                if hasattr(start, 'forward_item') and hasattr(start.forward_item, 'road_type'):
                    if start.forward_item.road_type == 'highway':
                        line_color = HIGHWAY_COLOR
                        line_width = 4
                    else:
                        line_color = RURAL_COLOR
                        line_width = 2
                else:
                    line_color = PREFAB_COLOR
                    line_width = 3

                # Draw connection line with navigation points
                pygame.draw.line(self.screen, line_color, start_pos, end_pos, line_width)
                if hasattr(start, 'nav_points'):
                    for point in start.nav_points:
                        point_pos = self._world_to_screen(point[0], point[2])
                        pygame.draw.circle(self.screen, (255, 255, 0), point_pos, 2)

                # Draw node circles with IDs
                pygame.draw.circle(self.screen, (255, 0, 0), start_pos, 5)
                font = pygame.font.Font(None, 24)
                text = font.render(str(start.uid), True, (255, 255, 255))
                self.screen.blit(text, (start_pos[0] + 10, start_pos[1] - 10))

            # Draw last node
            last_pos = self._world_to_screen(route[-1].x, route[-1].z)
            pygame.draw.circle(self.screen, (255, 0, 0), last_pos, 5)
            font = pygame.font.Font(None, 24)
            text = font.render(str(route[-1].uid), True, (255, 255, 255))
            self.screen.blit(text, (last_pos[0] + 10, last_pos[1] - 10))

            # Draw route statistics
            if show_stats:
                font = pygame.font.Font(None, 24)
                stats_text = [
                    f"Routing Mode: {mode}",
                    f"Total Distance: {total_distance:.1f}m",
                    f"Nodes: {len(route)}",
                    f"Start: {route[0].uid}",
                    f"End: {route[-1].uid}"
                ]
                for i, text in enumerate(stats_text):
                    rendered = font.render(text, True, (255, 255, 255))
                    self.screen.blit(rendered, (10, 10 + i * 25))

        except Exception as e:
            logging.error(f"Error drawing route: {e}")

        # Update display
        pygame.display.flip()

        # Update display
        pygame.display.flip()

    def auto_adjust_view(self, route: List[Node], padding: float = 0.1):
        """Automatically adjust the view to fit the entire route."""
        if not route:
            return

        # Find bounds
        min_x = min(node.x for node in route)
        max_x = max(node.x for node in route)
        min_z = min(node.z for node in route)
        max_z = max(node.z for node in route)

        # Calculate required scale
        width = max_x - min_x
        height = max_z - min_z

        if width == 0 or height == 0:
            return

        # Add padding
        width *= (1 + padding)
        height *= (1 + padding)

        # Calculate scale to fit screen
        scale_x = self.screen_width / width
        scale_y = self.screen_height / height
        self.scale = min(scale_x, scale_y)

        # Center the route
        self.offset_x = -(min_x + max_x) / 2
        self.offset_y = -(min_z + max_z) / 2

    def draw_navigation_lanes(self, nav_lanes: List['NavigationLane'], mode: str = 'shortest'):
        """Draw navigation lanes with their points."""
        if not nav_lanes:
            return

        try:
            # Clear screen
            self.screen.fill((0, 0, 0))

            # Draw each navigation lane
            total_distance = 0
            for lane in nav_lanes:
                points = lane.lane.points
                for i in range(len(points) - 1):
                    start_pos = self._world_to_screen(points[i][0], points[i][2])
                    end_pos = self._world_to_screen(points[i+1][0], points[i+1][2])

                    # Draw lane segment
                    pygame.draw.line(self.screen, (0, 255, 0), start_pos, end_pos, 2)
                    # Draw navigation points
                    pygame.draw.circle(self.screen, (255, 255, 0), start_pos, 2)

                    # Calculate segment distance
                    total_distance += DistanceBetweenPoints(points[i], points[i+1])

            # Draw last point of last lane
            if nav_lanes and nav_lanes[-1].lane.points:
                last_point = nav_lanes[-1].lane.points[-1]
                last_pos = self._world_to_screen(last_point[0], last_point[2])
                pygame.draw.circle(self.screen, (255, 255, 0), last_pos, 2)

            # Draw statistics
            font = pygame.font.Font(None, 24)
            stats_text = [
                f"Routing Mode: {mode}",
                f"Total Distance: {total_distance:.1f}m",
                f"Navigation Lanes: {len(nav_lanes)}"
            ]
            for i, text in enumerate(stats_text):
                rendered = font.render(text, True, (255, 255, 255))
                self.screen.blit(rendered, (10, 10 + i * 25))

            pygame.display.flip()

        except Exception as e:
            logging.error(f"Error drawing navigation lanes: {e}")

    def close(self):
        """Close the visualization window."""
        pygame.quit()
