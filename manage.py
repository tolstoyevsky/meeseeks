"""Module collect installed apps and run. """

import asyncio

from meeseeks.core import MeeseeksCore


async def main() -> None:
    """Collect and run applications. """

    await MeeseeksCore().run()

if __name__ == '__main__':
    asyncio.run(main())
