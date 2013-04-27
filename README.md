ledani
================================================================================

A way to automatically indicate who is home.

Currently, the only way to obtain presence information is by polling a
local wifi network (in ledani.py). The other side of the equation
relies on a raspberry pi to control LEDs, for which an enclosure
design is provided (in widget/).

BUILD
--------------------------------------------------------------------------------
Obtain some materials.
 - A raspi
 - A wifi adapter compatible with the raspi
 - 24x12in of 1/4 or 1/8in wood
 - LEDs
 - Wires
 - Low valued resistors (100-1kohms)
 - Parchment paper (wax paper)
 - Shellac
 - Zip tie

Use the design drawings (made with Inkscape) in `widget/` to laser cut
an enclosure. You may have to re-draw the design to accomdate however
many people you want to indicate for, and compensate for the kerf on
your laser cutter (getting the tightest fit might not be the best
thing to do, given I had to have a little loose play in order to snap
the pieces together while incremently gluing everything
together). Assemble the enclosure.

Cut out a standard-sized piece of parchment paper, and print
(inkjet/laser) whatever icons for each indicatee on it (see an
example/template soon to be included in the repo). The wax paper
provides diffusion, and the icon is, well... iconic. Spray some
shellac over the icons to keep the printed icons from rubbing off the
wax paper, and cut out the icons so they fit in the enclosure windows.

Now, wire up the LEDs in series with the resistors, wiring them
through the holes, using glue to hold everything together (with a
possible extension using PCBs to tie everything together in a neater fashion).

NOTE: There's a circuit/pcb for the LEDs http://www.circuits.io/circuits/3238

USAGE
--------------------------------------------------------------------------------
While you're doing the BUILD, ssh into the raspi and clone the repo
into it. Make a `virtualenv` in the repo directory, and run `pip -r
requirements.txt`. Copy the `ledani.example.conf` to `ledani.conf` and
make the necessary edits, and configure your crontab to execute
`ledani.py` on a regular basis.

TODO
--------------------------------------------------------------------------------
Possible future extensions:

 - Service to make identifying who's who through the poller.
 - Make mobile apps to update location
 - Use RFID
 - PCB for cleaner LED situation

ETYMOLOGY
--------------------------------------------------------------------------------
Name comes from the indicator method (LEDs) and the lojban zdani (home).
