"""Interactive map entities/players!

Note:
  Could even be something like a sign! Or the human player.

"""

import pygame

from hypatia import constants
from hypatia import actor


class HumanPlayer(actor.Actor):
    """A human-controlled actor.

    This class represents an actor under the control of the player.
    Basically, this class represents the "player" or the "main
    character" of a game.

    See Also:
        :class:`actor.Actor`
        :class:`NPC`

    """

    def __init__(self, *args, **kwargs):
        actor.Actor.__init__(self, *args, **kwargs)

    # NOTE: outdated/needs to be updated for velocity
    def move(self, game, direction):
        """Modify human player's positional data legally (check
        for collisions).
        Note:
          Will round down to nearest probable step
          if full step is impassable.
          Needs to use velocity instead...
        Args:
          direction (constants.Direction):

        """

        self.walkabout.direction = direction

        # hack for incorporating new velocity system, will update later
        if direction in (constants.Direction.north, constants.Direction.south):
            planned_movement_in_pixels = self.velocity.y
        else:
            planned_movement_in_pixels = self.velocity.x

        adj_speed = game.screen.time_elapsed_milliseconds / 1000.0
        iter_pixels = max([1, int(planned_movement_in_pixels)])

        # test a series of positions
        for pixels in range(iter_pixels, 0, -1):
            # create a rectangle at the new position
            new_topleft_x, new_topleft_y = self.walkabout.topleft_float

            # what's going on here
            if pixels == 2:
                adj_speed = 1

            if direction == constants.Direction.north:
                new_topleft_y -= pixels * adj_speed
            elif direction == constants.Direction.east:
                new_topleft_x += pixels * adj_speed
            elif direction == constants.Direction.south:
                new_topleft_y += pixels * adj_speed
            elif direction == constants.Direction.west:
                new_topleft_x -= pixels * adj_speed

            destination_rect = pygame.Rect((new_topleft_x, new_topleft_y),
                                           self.walkabout.size)
            collision_rect = self.walkabout.rect.union(destination_rect)

            if not game.scene.collide_check(collision_rect):
                # we're done, we can move!
                new_topleft = (new_topleft_x, new_topleft_y)
                self.walkabout.action = constants.Action.walk
                animation = self.walkabout.current_animation()
                self.walkabout.size = animation.largest_frame_size()
                self.walkabout.rect = destination_rect
                self.walkabout.topleft_float = new_topleft

                return True

        # never found an applicable destination
        self.walkabout.action = constants.Action.stand

        return False


class NPC(actor.Actor):
    """A computer controlled actor.

    This class represents all actors under the control of the engine,
    or to put it another way, all actors which the player **does not**
    control.

    Attributes:
        active (bool): True if the NPC is active, false otherwise.
            By default the attribute is False.  When set to True it
            will invoke the on_activation() method for that NPC.
            Likewise, when assigned the False value the object will
            invoke its on_deactivation() method.

    Examples:
        >>> npc = NPC()
        >>> npc.active
        False
        >>> npc.active = True
        >>> npc.active
        True

        >>> class Door(NPC):
        ...     def __init__(self, *args, **kwargs):
        ...         NPC.__init__(self, *args, **kwargs)
        ...         self.locked = False
        ...
        ...     def on_activation(self): self.locked = True
        ...
        ...     def on_deactivation(self): self.locked = False

        >>> door = Door()
        >>> door.locked
        False
        >>> door.active
        False
        >>> door.active = True
        >>> door.locked
        True
        >>> door.active = False
        >>> door.locked
        False

    See Also:
        :class:`actor.Actor`
        :class:`HumanPlayer`

    """

    def __init__(self, *args, **kwargs):
        actor.Actor.__init__(self, *args, **kwargs)
        self._active = False

    def __str__(self):
        """Returns a string representation of the NPC

        This representation is meant for debugging purposes only.  It
        does not return a valid Python expression and thus cannot
        recreate instances of the NPC class.

        Examples:
            >>> npc = NPC()
            >>> str(npc)
            '<Inactive NPC>'
            >>> npc.active = True
            >>> str(npc)
            '<Active NPC>'

        """
        if self.active is True:

            return "<Active NPC>"

        else:

            return "<Inactive NPC>"

    @property
    def active(self):
        """A boolean indicating whether or not the NPC is active.

        Assigning this property a True value will invoke the object's
        on_activation() method.  Likewise, assigning False will invoke
        its on_deactivation() method.

        """

        return self._active

    @active.setter
    def active(self, status):
        """Sets the active status for the NPC to True or False.

        Args:
            status (bool): The new active status.

        Raises:
            ValueError: If the status argument is not True or False.
                Arguably this could be a TypeError instead

        """
        self._active = status

        if status is True:
            self.on_activation()
        elif status is False:
            self.on_deactivation()
        else:

            raise ValueError("Status must be boolean True or False")

    @active.deleter
    def active(self):
        """Deletes the active property, which is always an error because an
        NPC must always have the active property.  Therefore this
        operation actually does nothing but raise an error.

        Raises:
            TypeError

        """

        raise TypeError("Cannot delete the 'active' property of an NPC")

    def on_activation(self):
        """Perform any necessary logic when the NPC becomes active.

        Whenever the active property of the NPC is set to True the
        object invokes this method.  By default the method is a no-op.

        """
        pass

    def on_deactivation(self):
        """Performs any necessary logic when we deactivate the NPC.

        When the active property is set to False the object invokes
        this method, which should perform anything appropriate for
        deactivating that object, e.g. removing it from the game.  By
        default, however, this method is a no-op.

        """
        pass
