# html.H4(className='datasets', children=_('Parameters description')),
                        #         html.H6(_("Operational parameters")),
                        #         dcc.Markdown(_('''
                        # - Delay at departure: delay at departure needed for the operator to set up
                        # flight information for the drone then for the fire station where the drone is stationed
                        # to launch it.
                        # - Delay on arrival: delay on arrival needed for the drone to narrow its landing and for
                        # the bystander to catch the AED.
                        # - Delay between detection of unconsciousness and OHCA detection:  mean time spent between
                        # unconsciousness and OHCA detection by emergency call dispatchers. Unconsciousness detection
                        # activates BLS teams whereas drones are activated only at OHCA detection.
                        # - Rate of OHCA at home, which are detected by call center operators: when the OHCA is not
                        # detected by the emergency dispatchers no drone is sent.
                        # - Rate of OHCA in the streets, which are detected by call center operators: when the OHCA is
                        # not detected by the emergency dispatchers no drone is sent.
                        # - Rate of OHCA at home, which only have one witness alone: The simulation requires at least
                        # two witnesses for OHCA at home : one to stay near the victim, the other to go out in the
                        # street to get the AED brought by drone.
                        # ''')),
                        #         html.H6(_("Drone parameters")),
                        #         dcc.Markdown(_('''
                        # - Initial drone location : where drones are stationed. The simulator selects
                        #  the closest available drone (as the crow flies).
                        #  - Max drone speed: maximum horizontal speed.
                        #  - Drone's acceleration time: time needed for the drone to reach its
                        #       maximum horizontal speed.
                        #  - Drone's vertical speed: maximum vertical speed. It is assumed that the time
                        #        needed for the drone to reach this speed is negligible.
                        # - Drone's cruise altitude: horizontal cruise altitude.
                        # - Unavailability of the drone after a run: time needed after a run for the
                        #       drone to be available again. It accounts for the time spent on the OHCA
                        #       location and the time of refurbishment and rehabilitation of equipment.
                        # - Flying restricted to aeronautical day: whether the drone can only fly
                        #       during the aeronautical day or not.
                        #  ''')),


# dbc.Col(children=_(
#     'This graph shows the time difference between the simulated time to arrival of a '
#     'drone and the actual time of arrival of the BLS team sent for every intervention. '
#     'On the right hand side (positive values) a drone would have been faster by the '
#     'number of seconds shown by the vertical bar. On the left hand side (negative '
#     'values) the BLS team would have been faster again by the number of seconds shown '
#     'by the vertical bar. Grey bars correspond to interventions for which a drone '
#     'would not be sent, vertical values are the actual BLS team time to arrival.'
# )),