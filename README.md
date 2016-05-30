runner
======

runner simply takes a list of tasks and executes one after the other. The only feature is that before each task it checks whether it should cancel instead. Currently the cancellation condition is hard-coded and checks whether the message of the day contains the word "reboot".

Uses

* <https://github.com/scrapy/queuelib>
