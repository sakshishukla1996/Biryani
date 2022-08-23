from services.policy import HandcraftedPolicy


class RestaurantPolicy(HandcraftedPolicy):
    def __init__(self, domain, logger=DiasysLogger()):
        # only calls super class' constructor
        super(RestaurantPolicy, self).__init__(domain, debug_logger=logger)

    def _next_action(self, beliefstate):
        pass
