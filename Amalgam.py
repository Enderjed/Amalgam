import math
 
from rlbot.agents.base_agent import BaseAgent, SimpleControllerState
from rlbot.utils.structures.game_data_struct import GameTickPacket
 
 
 
 
class Atba2(BaseAgent):
 
    def initialize_agent(self):
        self.jump = 0
        self.timejump = 0
        self.jumpheight = 0
        self.dodge = 0
        self.timedodge = 0
        self.j = 0
 
    def get_output(self, packet):
 
        game = self.convert_packet_to_v3(packet)
 
        pIndex = self.index
        player = game.gamecars[pIndex] # 0 for p1, 1 for p2
        ball = game.gameball
        time = game.gameInfo.TimeSeconds
 
        ball_Location = _predictive(player,ball.Location,ball.Velocity) 
 
        dist = math.sqrt((player.Location.X - ball.Location.X)**2 + (player.Location.Y - ball.Location.Y)**2 + (player.Location.Z - ball.Location.Z)**2 )
        vel = abs(player.Velocity.X - ball.Velocity.X) + abs(player.Velocity.Y - ball.Velocity.Y) + abs(player.Velocity.Z- ball.Velocity.Y)
        x,y,z = local(ball_Location,[0,0,0],player.Rotation)
        _px,_py,_pz = local(player.Velocity,[0,0,0],player.Rotation)
        _bx,_by,_bz = local(ball.Velocity,[0,0,0],player.Rotation)
        _x,_y,_z = _px-_bx,_py-_by,_pz-_bz
        d,a,i = _spherical([x,y,z])
        r = _roll(player)
        _i,_r,_a = local(player.AngularVelocity,[0,0,0],player.Rotation)
        
        b_radius = 0.3048
        if z >210:
            b_radius = 0.6
        if z >450:
            b_radius = 0.7
        if z> 1200:
            b_radius = 0.5
 
 
        if (abs(a)>0.8 and _py>1000) or ( (z*b_radius)**2 > (d**2 - z**2) and abs(a) < 0.26 ) or (abs(a) > 0.75  and d < 700 ) or (d > z*2.8 and abs(a) < 0.03 and _y>1500 and z>500 and d<600) or (abs(a)>0.4 and _y>800 and abs(a)<0.75):
            Backwards = 32768
            Throttle = 0
            # if (d < 250 or d > 350) and abs(_y)<600 : a*=-1
        else : 
            Throttle = 32768
            Backwards = 0
 
        if abs(a) < 0.24 and Throttle > 32000 and _py < 2290 and d > 140  and (abs(0.5-abs(i))>0.3 or (player.Location.Z<25 and _y<0)) :
            Boost = 1
        else :
            Boost = 0
 
        if abs(a) > 0.46 and abs(a) < 0.8 and player.Location.Z < 20:
            powerslide = 1
        else:
            powerslide = 0
 
        h_i = 0.01*(0.5-abs(i))
        h_r = 0.05*(1-abs(r))
 
        if player.Location.Z>20:
            h_a = 0.05*(1-abs(a))
        else:
            h_a = 0.095*(1-abs(a))
 
        if (a - _a/11.25)*math.copysign(1,a) < 0 and abs(a)>0.01:
            if (player.Location.Z > 20 and on_wall(player.Location)==False) :
                a *= -1
        
        if (r - _r/22)*math.copysign(1,r) < 0 :
                r *= -1
 
        if (i + _i/23)*math.copysign(1,i) < 0 :
                i *= -1
 
        a_turn = (math.copysign( abs(a)**(1-abs(a)**h_a), a ) + 1 ) *16383
        i_turn = (math.copysign( abs(i)**(1-abs(i)**h_i), -i ) + 1 ) *16383
        r_turn = (math.copysign( abs(r)**(1-abs(r)**h_r), -r ) + 1 ) *16383
 
        if (abs(0.5-abs(a))>0.4 and abs(0.5-abs(i))>0.15 and abs(r)>0.3 and player.Location.Z>30 and on_wall(player.Location)==False 
            or ((25 < player.Location.Z < 250 and player.Velocity.Z < -400) or (player.Location.Z>1900 and player.Velocity.Z > 350)) and d > 400 and abs(r)>0.15 ): 
            # a_turn = r_turn
            # powerslide = 1
            0
        else:
            r_turn = 16383
 
 
        jump = 0
 
        if z > 155 and abs(a) < 0.05 and _y > -350 and d <z*(1.1+player.Boost/60) and z< 700 +player.Boost*14:
            Throttle = 0
            Backwards = 32768
            if self.jump == 0 and int(time*100)%2==0:
                self.jump = 1
                self.timejump = time
                # print("Double jump",int(time*10))
 
        # print(_py)
        if (d <= 220 ) and ( dist < 820 and vel > 0.600) and abs(z) <= 85 and abs(player.Location.Z-ball.Location.Z)< 100 and abs(0.5 -abs(i)) >0.15 :
            # print("Dodge Condition")
            if (player.Location.Z > 20 and self.dodge == 0) :
                # a_turn = 16383
                # if player.ball_Locationn.Z <40 :i_turn = 32768
                if (player.Location.Z >50 or (dist<110 and z<60)) :
                    # print("Dodging",int(time))
                    if self.dodge == 0 :
                        # jump = 1
                        self.dodge = 1
                        self.timedodge = time
            if  player.Location.Z < 20 or (on_wall(player.Location)==True and z>60) :
                if self.jump == 0 :
                    # print("self.jump")
                    self.jump = 1
                    self.timejump = time-0.19
 
 
 
        if (z>1350 or ((d<z*1.5 or vel<400) and player.Location.Z<500 and abs(a) < 0.15 and ball.Location.Z < 500)) and on_wall(player.Location)==True and player.Location.Z>60 and (abs(0.5-abs(a))>0.25 or d>2500) : #preventing the bot from staying on the walls
            if self.jump==0:
                self.jump = 1
                self.timejump = time
                # print('wall, jump')
 
        if ( (time > self.timejump +0.25 or z<20 ) and self.timejump !=0 and self.jump == 1  ):
            # print('reset')
            self.jump = 0
            self.timejump = time
 
        if ( time < self.timejump +0.05 ):
            a_turn = 16383
            i_turn = 16383
 
        if self.jump == 1 :
            if self.j == self.jump:
                jump = 1
        else: 
            jump = 0
        
        if player.Location.Z<250 and time < self.timedodge +abs(1-a/2)*0.66 and self.timedodge !=time and player.Location.Z > 34 :
            a_turn = 16383
            i_turn = 16383
 
        if time < self.timedodge +0.05 and self.timedodge !=time and player.Location.Z > 34 :
            i_turn =  abs(a)*32768
            a_turn = abs(Range180(a+0.5,1))*32768
            
        if self.dodge == 1 :
            self.jump=0
            jump = 1
            # print("Dodge",int(time))
            # print(a*180)  
            i_turn =  abs(a)*32768  
            a_turn = abs(Range180(a+0.5,1))*32768
            self.timedodge = time
            self.dodge = 0
 
 
 
 
        self.j = self.jump
 
        # return[int(a_turn), int(i_turn), Throttle, Backwards, jump, Boost, powerslide]
        output = [(Throttle-Backwards)/U,a_turn/(U/2)-1,i_turn/(U/2)-1,a_turn/(U/2)-1,r_turn/(U/2)-1,jump,Boost,powerslide]
 
        return self.convert_output_to_v4(output)
        def get_game_score(packet: GameTickPacket):
    score = [0, 0]  # Index 0 is team0, index 1 is team1
 
    for car in packet.game_cars:
        score[car.team] += car.score_info.goals
 
    return score
 
 
class QuickChatExampleAgent(BaseAgent):
    def initialize_agent():
        self.previous_frame_opponent_score = 0
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        controller = SimpleControllerState()
 
        current_score = get_game_score(packet)
        if self.previous_frame_opponent_score < current_score[not self.team]:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_NiceShot)
 
        self.previous_frame_opponent_score = current_score[not self.team]
 
        return controller
 
    def handle_quick_chat(self, index, team, quick_chat):
        if team != self.team and quick_chat == QuickChats.Compliments_NiceShot:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_Thanks)
            class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
 
        # Contants
        self.DODGE_TIME = 0.2
        self.DISTANCE_TO_DODGE = 500
        self.DISTANCE_FROM_BALL_TO_BOOST = 1500  # The minimum distance the ball needs to be away from the bot for the bot to boost
        # The angle (from the front of the bot to the ball) at which the bot should start to powerslide.
        self.POWERSLIDE_ANGLE = math.radians(170)
 
        # Game values
        self.bot_pos = None
        self.bot_yaw = None
 
        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0
 
    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)
 
        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw
 
        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi
 
        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0
 
        self.controller.handbrake = abs(math.degrees(angle_front_to_target)) < self.POWERSLIDE_ANGLE
 
    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1
 
            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location
 
        # Boost when ball is far enough away
        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST
 
        # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        self.controller.throttle = 1
 
        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)
 
        # Boost on kickoff
        if ball_pos.x == 0 and ball_pos.x == 0:
            self.aim(ball_pos.x, ball_pos.x)
            self.controller.boost = True
 
        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0
 
        self.check_for_dodge()
 
        return self.controller
        class diabloBot(BaseAgent):
    def __init__(self, name, team, index):
        Game.set_mode("soccar")
        self.game = Game(index, team)
        self.index = index
        self.name = name
        self.team = team
 
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.me = physicsObject()
        self.ball = physicsObject()
        self.me.team = self.team
        self.allies = []
        self.enemies = []
        self.start = 5
        self.flipStart = 0
        self.flipping = False
        self.controller = None
        self.flipTimer = time.time()
        self.activeState = Kickoff(self)
        self.gameInfo = None
        self.onSurface = False
        self.boosts = []
        self.fieldInfo = []
        self.positions = []
        self.time = 0
        self.deltaTime = 0
        self.maxSpd = 2200
        self.ballPred = []
        self.selectedBallPred = None
        self.ballDelay = 0
        self.renderCalls = []
        self.ballPredObj = None
        self.carHeight = 84
        self.forward = True
        self.velAngle = 0
        self.onWall = False
        self.stateTimer = time.time()
        self.contested = True
        self.flipTimer = time.time()
        self.goalPred = None
 
    def getActiveState(self):
        if type(self.activeState) == JumpingState:
            return 0
        if type(self.activeState) == Kickoff:
            return 1
        if type(self.activeState) == GetBoost:
            return 2
        if type(self.activeState) == Dribble:
            return 3
        if type(self.activeState) == GroundShot:
            return 4
        if type(self.activeState) == GroundDefend:
            return 5
        if type(self.activeState) == halfFlip:
            return 6
 
    def setHalfFlip(self):
        self.activeState = halfFlip(self)
 
    def determineFacing(self):
        offset = self.me.location + self.me.velocity
        loc = toLocal(offset,self.me)
        angle = math.degrees(math.atan2(loc[1],loc[0]))
        if angle < -180:
            angle += 360
        if angle > 180:
            angle -= 360
 
        if abs(angle) >150 and self.getCurrentSpd() > 200:
            self.forward = False
        else:
            self.forward = True
 
        self.velAngle = angle
 
 
 
    def setJumping(self,targetType):
        _time = time.time()
        if _time - self.flipTimer > 2:
            if self.me.location[2] > 250:
                self.activeState = JumpingState(self, -1)
            else:
                self.activeState = JumpingState(self, targetType)
            self.flipTimer = _time
 
    def setDashing(self,target):
        self.activeState = WaveDashing(self,target)
 
 
    def getCurrentSpd(self):
        return Vector(self.me.velocity[:2]).magnitude()
 
    def updateSelectedBallPrediction(self,ballStruct):
        x = physicsObject()
        x.location = Vector([ballStruct.physics.location.x, ballStruct.physics.location.y, ballStruct.physics.location.z])
        x.velocity = Vector([ballStruct.physics.velocity.x, ballStruct.physics.velocity.y, ballStruct.physics.velocity.z])
        x.rotation = Vector([ballStruct.physics.rotation.pitch, ballStruct.physics.rotation.yaw, ballStruct.physics.rotation.roll])
        x.avelocity = Vector([ballStruct.physics.angular_velocity.x, ballStruct.physics.angular_velocity.y, ballStruct.physics.angular_velocity.z])
        x.local_location = localizeVector(x.location, self.me)
        self.ballPredObj = x
 
 
 
 
    def preprocess(self, game):
        self.ballPred = self.get_ball_prediction_struct()
        self.players = [self.index]
        self.game.read_game_information(game,
                                        self.get_rigid_body_tick(),
                                        self.get_field_info())
        car = game.game_cars[self.index]
        self.me.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
        self.me.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
        self.me.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
        self.me.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
        self.me.boostLevel = car.boost
        self.onSurface = car.has_wheel_contact
        self.deltaTime = clamp(1/60,1/300,self.game.time_delta)
 
 
        ball = game.game_ball.physics
        self.ball.location = Vector([ball.location.x, ball.location.y, ball.location.z])
        self.ball.velocity = Vector([ball.velocity.x, ball.velocity.y, ball.velocity.z])
        self.ball.rotation = Vector([ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll])
        self.ball.avelocity = Vector([ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z])
        self.me.matrix = rotator_to_matrix(self.me)
        self.ball.local_location = localizeVector(self.ball.location,self.me)
        self.determineFacing()
        self.onWall = False
        if self.onSurface:
            if self.me.location[2] > 70:
                self.onWall = True
 
        self.allies.clear()
        self.enemies.clear()
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                _obj = physicsObject()
                _obj.index = i
                _obj.team = car.team
                _obj.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
                _obj.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
                _obj.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
                _obj.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
                _obj.boostLevel = car.boost
                _obj.local_location = localizeVector(_obj,self.me)
 
                if car.team == self.team:
                    self.allies.append(_obj)
                else:
                    self.enemies.append(_obj)
        self.gameInfo = game.game_info
        self.boosts.clear()
        self.fieldInfo = self.get_field_info()
        for index in range(len(self.fieldInfo.boost_pads)):
            packetBoost = game.game_boosts[index]
            fieldInfoBoost = self.fieldInfo.boost_pads[index]
            self.boosts.append(Boost_obj([fieldInfoBoost.location.x,fieldInfoBoost.location.y,fieldInfoBoost.location.z],fieldInfoBoost.is_full_boost, packetBoost.is_active))
 
        ballContested(self)
        self.goalPred = None
 
 
 
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        if len(self.allies) >=1:
            teamStateManager(self)
        else:
            soloStateManager(self)
        action = self.activeState.update()
 
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(100, 100, 1, 1, str(type(self.activeState)), self.renderer.white())
 
        for each in self.renderCalls:
            each.run()
        self.renderer.end_rendering()
        self.renderCalls.clear()
 
        return action
    
 
 
class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
 
        # Contants
        self.DODGE_TIME = 0.2
        self.DISTANCE_TO_DODGE = 500
        self.DISTANCE_FROM_BALL_TO_BOOST = 1500  # The minimum distance the ball needs to be away from the bot for the bot to boost
        # The angle (from the front of the bot to the ball) at which the bot should start to powerslide.
        self.POWERSLIDE_ANGLE = math.radians(170)
 
        # Game values
        self.bot_pos = None
        self.bot_yaw = None
 
        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0
 
    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)
 
        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw
 
        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi
 
        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0
 
        self.controller.handbrake = abs(math.degrees(angle_front_to_target)) < self.POWERSLIDE_ANGLE
 
    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1
 
            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location
 
        # Boost when ball is far enough away
        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST
 
        # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        self.controller.throttle = 1
 
        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)
 
        # Boost on kickoff
        if ball_pos.x == 0 and ball_pos.x == 0:
            self.aim(ball_pos.x, ball_pos.x)
            self.controller.boost = True
 
        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0
 
        self.check_for_dodge()
 
        return self.controller
        class diabloBot(BaseAgent):
    def __init__(self, name, team, index):
        Game.set_mode("soccar")
        self.game = Game(index, team)
        self.index = index
        self.name = name
        self.team = team
 
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.me = physicsObject()
        self.ball = physicsObject()
        self.me.team = self.team
        self.allies = []
        self.enemies = []
        self.start = 5
        self.flipStart = 0
        self.flipping = False
        self.controller = None
        self.flipTimer = time.time()
        self.activeState = Kickoff(self)
        self.gameInfo = None
        self.onSurface = False
        self.boosts = []
        self.fieldInfo = []
        self.positions = []
        self.time = 0
        self.deltaTime = 0
        self.maxSpd = 2200
        self.ballPred = []
        self.selectedBallPred = None
        self.ballDelay = 0
        self.renderCalls = []
        self.ballPredObj = None
        self.carHeight = 84
        self.forward = True
        self.velAngle = 0
        self.onWall = False
        self.stateTimer = time.time()
        self.contested = True
        self.flipTimer = time.time()
        self.goalPred = None
 
    def getActiveState(self):
        if type(self.activeState) == JumpingState:
            return 0
        if type(self.activeState) == Kickoff:
            return 1
        if type(self.activeState) == GetBoost:
            return 2
        if type(self.activeState) == Dribble:
            return 3
        if type(self.activeState) == GroundShot:
            return 4
        if type(self.activeState) == GroundDefend:
            return 5
        if type(self.activeState) == halfFlip:
            return 6
 
    def setHalfFlip(self):
        self.activeState = halfFlip(self)
 
    def determineFacing(self):
        offset = self.me.location + self.me.velocity
        loc = toLocal(offset,self.me)
        angle = math.degrees(math.atan2(loc[1],loc[0]))
        if angle < -180:
            angle += 360
        if angle > 180:
            angle -= 360
 
        if abs(angle) >150 and self.getCurrentSpd() > 200:
            self.forward = False
        else:
            self.forward = True
 
        self.velAngle = angle
 
 
 
    def setJumping(self,targetType):
        _time = time.time()
        if _time - self.flipTimer > 2:
            if self.me.location[2] > 250:
                self.activeState = JumpingState(self, -1)
            else:
                self.activeState = JumpingState(self, targetType)
            self.flipTimer = _time
 
    def setDashing(self,target):
        self.activeState = WaveDashing(self,target)
 
 
    def getCurrentSpd(self):
        return Vector(self.me.velocity[:2]).magnitude()
 
    def updateSelectedBallPrediction(self,ballStruct):
        x = physicsObject()
        x.location = Vector([ballStruct.physics.location.x, ballStruct.physics.location.y, ballStruct.physics.location.z])
        x.velocity = Vector([ballStruct.physics.velocity.x, ballStruct.physics.velocity.y, ballStruct.physics.velocity.z])
        x.rotation = Vector([ballStruct.physics.rotation.pitch, ballStruct.physics.rotation.yaw, ballStruct.physics.rotation.roll])
        x.avelocity = Vector([ballStruct.physics.angular_velocity.x, ballStruct.physics.angular_velocity.y, ballStruct.physics.angular_velocity.z])
        x.local_location = localizeVector(x.location, self.me)
        self.ballPredObj = x
 
 
 
 
    def preprocess(self, game):
        self.ballPred = self.get_ball_prediction_struct()
        self.players = [self.index]
        self.game.read_game_information(game,
                                        self.get_rigid_body_tick(),
                                        self.get_field_info())
        car = game.game_cars[self.index]
        self.me.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
        self.me.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
        self.me.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
        self.me.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
        self.me.boostLevel = car.boost
        self.onSurface = car.has_wheel_contact
        self.deltaTime = clamp(1/60,1/300,self.game.time_delta)
 
 
        ball = game.game_ball.physics
        self.ball.location = Vector([ball.location.x, ball.location.y, ball.location.z])
        self.ball.velocity = Vector([ball.velocity.x, ball.velocity.y, ball.velocity.z])
        self.ball.rotation = Vector([ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll])
        self.ball.avelocity = Vector([ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z])
        self.me.matrix = rotator_to_matrix(self.me)
        self.ball.local_location = localizeVector(self.ball.location,self.me)
        self.determineFacing()
        self.onWall = False
        if self.onSurface:
            if self.me.location[2] > 70:
                self.onWall = True
 
        self.allies.clear()
        self.enemies.clear()
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                _obj = physicsObject()
                _obj.index = i
                _obj.team = car.team
                _obj.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
                _obj.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
                _obj.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
                _obj.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
                _obj.boostLevel = car.boost
                _obj.local_location = localizeVector(_obj,self.me)
 
                if car.team == self.team:
                    self.allies.append(_obj)
                else:
                    self.enemies.append(_obj)
        self.gameInfo = game.game_info
        self.boosts.clear()
        self.fieldInfo = self.get_field_info()
        for index in range(len(self.fieldInfo.boost_pads)):
            packetBoost = game.game_boosts[index]
            fieldInfoBoost = self.fieldInfo.boost_pads[index]
            self.boosts.append(Boost_obj([fieldInfoBoost.location.x,fieldInfoBoost.location.y,fieldInfoBoost.location.z],fieldInfoBoost.is_full_boost, packetBoost.is_active))
 
        ballContested(self)
        self.goalPred = None
 
 
 
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        if len(self.allies) >=1:
            teamStateManager(self)
        else:
            soloStateManager(self)
        action = self.activeState.update()
 
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(100, 100, 1, 1, str(type(self.activeState)), self.renderer.white())
 
        for each in self.renderCalls:
            each.run()
        self.renderer.end_rendering()
        self.renderCalls.clear()
 
        return action
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
 
def xy_to_polar_coordinates(x,y): 
    d = math.sqrt(x*x+y*y)
    a = math.atan2(y,x)
    return d,a
def polar_to_xy_coordinates(d,a): 
    x = d*math.cos(a)
    y = d*math.sin(a)
    return
 
def xyz_to_spherical_coordinates(x,y,z): 
    d = math.sqrt(x*x+y*y+z*z)
    try : i = math.acos(z/d)
    except ZeroDivisionError: i=0
    a = math.atan2(y,x)
    return d,a,i
def spherical_to_xyz_coordinates(d,a,id): 
    x = d*math.sin(i)*math.cos(a)
    y = d*math.sin(i)*math.sin(a)
    z = d*cos(i)
    return x,y,z
 
def global_to_local_xy_coordinates(x,y,ox,oy,rot): 
    _x = (x-ox)*math.cos(rot) + (y-oy)*math.sin(rot)
    _y = -(x-ox)*math.sin(rot) + (y-oy)*math.cos(rot)
    return _x,_y
def global_to_local_xyz_coordinates(x,y,z,ox,oy,oz,pitch,yaw,roll): 
 
    r1,r2,r3 = pitch,roll,yaw
 
    Rx  = np.array([[      1,             0,               0      ],
                    [      0,        math.cos(r1),  -math.sin(r1) ],
                    [      0,        math.sin(r1),   math.cos(r1) ]])
    Ry  = np.array([[ math.cos(r2),       0,         math.sin(r2) ],
                    [      0,             1,               0      ],
                    [-math.sin(r2),       0,         math.cos(r2) ]])
    Rz  = np.array([[ math.cos(r3),  -math.sin(r3),        0      ],
                    [ math.sin(r3),   math.cos(r3),        0      ],
                    [      0,                 0,           1      ]])
 
    R   = np.dot(Rz,Rx)
    R   = np.dot(R,Ry)
    R   = R.T
    V   = np.dot(R,np.array([x-ox,y-oy,z-oz]))
 
    return V
 
def vector(V): 
    a = np.zeros(shape=(3))
    try: a[0]=V[0]
    except: 
        try: a[0]=V.X
        except: a[0]=V.Pitch
    try: a[1]=V[1]
    except: 
        try: a[1]=V.Y
        except: a[1]=V.Yaw
    try: a[2]=V[2]
    except: 
        try: a[2]=V.Z
        except: 
            try : a[2]=V.Roll
            except : print("Type Invalid")
    return a
def local(P,oP,R): 
    P = vector(P)
    oP = vector(oP)
    R = rotations(vector(R))
    x,y,z = global_to_local_xyz_coordinates(P[0],P[1],P[2],oP[0],oP[1],oP[2],R[0],R[1],R[2])
    return x,y,z
def _spherical(P): 
    P = vector(P)
    d,i,a = xyz_to_spherical_coordinates(P[0],P[1],P[2])
    return d, Range180(i-math.pi/2,math.pi)/math.pi, Range180(a-math.pi/2,math.pi)/math.pi
def rotations(R): 
    p = R[0]/32768*math.pi
    y = Range180(R[1]-16384,32768)/32768*math.pi
    r = - R[2]/32768*math.pi
    return p,y,r
 
def _roll(player):
    x,y,z = player.Location.X, player.Location.Y, player.Location.Z
    _x,_y,_z = player.Velocity.X, player.Velocity.Y, player.Velocity.Z
    x_,y_,z_ = x+_x/1.5, y+_y/1.5, z+_z/1.5
    r,a,i = player.Rotation.Roll/32768*180,player.Rotation.Yaw/32768*180,player.Rotation.Pitch/32768*180
    a90 = Range180(a+90,180)
    if z_ > 50  :
        if abs(x_) > 4000 and abs(x)<4050 and abs(y_)<5000   :
            r = Range180(r-math.copysign(90,a*x),180)
        if abs(y_) > 5000 and abs(x)<4000 and abs(90-abs(a))>30:
            r = Range180(r-math.copysign(90,-a90*y),180)
        if z_ > 1700 :
            r = math.copysign(180-abs(r),-r)
    return r/180
 
def Range180(value,pi): 
    return value - math.copysign( (pi*2) * (abs(value)//pi) ,value)
def pos(v):
    if v>0: return v
    else  : return 0
 
def on_wall(Location): 
    Location = vector(Location) 
    return (( abs(Location[0]) > 4000-100  or  abs(Location[1]) > 5000-100 or ( abs(Location[0]) > 2900-80 and abs(Location[1]) > 4000-80)) or Location[2] > 1800) and abs(Location[1]<5150 and abs(Location[0]) <4150)
 
def _predictive(player,target_loc,target_vel): 
    target_loc, target_vel = vector(target_loc), vector(target_vel)
    dist = math.sqrt((player.Location.X - target_loc[0])**2 + (player.Location.Y - target_loc[1])**2 + (player.Location.Z - target_loc[2])**2 )
    _loc = vector([ target_loc[0] - player.Location.X,  target_loc[1] - player.Location.Y,  target_loc[2] - player.Location.Z  ])
    
    g = 0
    if player.Location.Z > 25 and on_wall(player.Location)==False and dist>1500 and target_loc[2]-player.Location.Z>500:
        g = 42  
    if target_loc[2]-player.Location.Z>700 and player.Location.Z <20 and dist < 5500 and dist>1500:
        g = -200
    
    player_vel = vector([player.Velocity.X,player.Velocity.Y,player.Velocity.Z*1-g])
    
    _target = _loc + target_vel*1*(dist/2450) - player_vel*1*(dist/2450)
 
    if target_loc[2] + target_vel[2]*1*dist/2500<60:
        _target[2]=(_target[2]-60)*(-0.1) +60
        # _target[1]=_loc[1] + ((target_vel[1] - p_vel[1])*0.9*dist/2500)
        # _target[0]=_loc[0] + ((target_vel[0] - p_vel[0])*0.9*dist/2500)
 
    return _target
    import math
 
try:
    import numpy as np
except ImportError:
    try:
        from pip import main as pipmain
    except ImportError:
        from pip._internal import main as pipmain
        pipmain(['install', 'numpy'])
    try:
        import numpy as np
    except ImportError:
        raise ImportError("Failed to install numpy automatically, please install manually using: 'pip install numpy'")
 
Bra71L=False
verbose = 0
 
RLBot_Version = 4
 
from rlbot.agents.base_agent import BaseAgent
 
class Dweller(BaseAgent):
    def get_output(self, packet):
        game = self.convert_packet_to_v3(packet)
        output = Process(game, self.index)
        return self.convert_output_to_v4(output)
 
class Agent:
   def __init__(self, name, team, index):
        self.index = index
   def get_output_vector(self, game):
        return Process(game,self.index)
 
class agent:
    def __init__(self, team):
        self.team = team
    def get_output_vector(self, sharedValue):
        game = sharedValue.GameTickPacket
        index = self.team!='blue'
        output=[16383, 16383, 0, 0, 0, 0, 0]
        if game.gameInfo.bRoundActive :
            output = Process(game,index)
        return output
 
U = 32768
tL=[0,0,0]
A,I,R,T,J,B,P=0,0,0,0,0,0,0
x,y,z,d,a,i = 0,0,0,0,0,0
xv,yv,zv=0,0,0
def Process(game,index):
 
    global A,I,R,T,J,B,P,U,pL,pR,pV,paV,poG,pB,pJ,pdJ,x,y,z,d,a,i,_px,_py,_pz,_i,_r,_a,_tx,_ty,_tz,_x,_y,_z,Game,ball,time,player,Index,t,nd,na,ni
    player,ball,Game,time,Index=game.gamecars[index],game.gameball,game,game.gameInfo.TimeSeconds,index
    pL,pR,pV,paV,poG,pB,pJ,pdJ=player.Location,player.Rotation,player.Velocity,player.AngularVelocity,player.bOnGround,player.Boost,player.bJumped,player.bDoubleJumped
    global _vd,_va,_vi,_tvd,_tva,_tvi,_pvd,_pva,_pvi,aiming
 
    t=Target(ball)
    _px,_py,_pz=local(pV,[0,0,0],pR)
    _tx,_ty,_tz=local(t.V,[0,0,0],pR)
    _x,_y,_z=_px-_tx,_py-_ty,_pz-_tz
    _vd,_va,_vi = spherical(_x,_y,_z)
    _tvd,_tva,_tvi = spherical(_tx,_ty,_tz)
    _pvd,_pva,_pvi = spherical(_px,_py,_pz)
    _i,_r,_a=local(paV,[0,0,0],pR)
    Strat()
    x,y,z=local(tL,pL,pR)
    if aiming : Aim()
    d,a,i=spherical(x,y,z)
    AIR()
    Thr()
    Jump()
 
    if RLBot_Version==4: output = int((A+1)*U/2), int((I+1)*U/2), int(T*U),int(-T*U), J, B, P
    else: output = T,A,I,A,R,J,B,P
 
    return output
    
 
class td:
    def __init__(self):
        self.L = v3()
        self.V = v3()
        self.aV= v3()
class v3:
    def __init__(self):
        self.X = 0
        self.Y = 0
        self.Z = 0
def a3(V): 
    a=np.zeros(shape=(3))
    try: a[0]=V[0]
    except: 
        try: a[0]=V.X
        except: a[0]=V.Pitch
    try: a[1]=V[1]
    except: 
        try: a[1]=V.Y
        except: a[1]=V.Yaw
    try: a[2]=V[2]
    except: 
        try: a[2]=V.Z
        except: a[2]=V.Roll
    return a
def Target(A):
    #A=[[10,20,3],[0,0,0],[0,0,0]] ## [Location,Velocity,AngularVelocity]
    t = td()
    try : t.L=A.Location
    except: 
        t.L.X=A[0][0]
        t.L.Y=A[0][1]
        t.L.Z=A[0][2]
    try: t.V=A.Velocity
    except: 
        try:
            t.V.X=A[1][0]
            t.V.Y=A[1][1]
            t.V.Z=A[1][2]
        except: t.V=[0,0,0]
    try :t.aV=A.AngularVelocity
    except:
        try:
            t.aV.X=A[2][0]
            t.aV.Y=A[2][1]
            t.aV.Z=A[2][2]
        except: t.aV=[0,0,0]
    return t
def Urotations(R): 
    global U
    p = R[0]/U*math.pi
    y = R180(R[1]-U/2,U)/U*math.pi
    r = - R[2]/U*math.pi
    return p,y,r
def spherical(x,y,z): 
    d = math.sqrt(x*x+y*y+z*z)
    if d!=0 : i = math.acos(z/d)
    else: i=0
    a = math.atan2(y,x)
    return d, R180(a-math.pi/2,math.pi)/math.pi, R180(i-math.pi/2,math.pi)/math.pi
def local(Target,Origin,Orientation,Urot=True): 
    Orientation = a3(Orientation)
    if Urot : Orientation=Urotations(Orientation)
    r1,r3,r2 = Orientation
 
    Rx  = np.array([[      1,             0,               0      ],
                    [      0,        math.cos(r1),  -math.sin(r1) ],
                    [      0,        math.sin(r1),   math.cos(r1) ]])
    Ry  = np.array([[ math.cos(r2),       0,         math.sin(r2) ],
                    [      0,             1,               0      ],
                    [-math.sin(r2),       0,         math.cos(r2) ]])
    Rz  = np.array([[ math.cos(r3),  -math.sin(r3),        0      ],
                    [ math.sin(r3),   math.cos(r3),        0      ],
                    [      0,                 0,           1      ]])
 
    R   = np.dot(Rz,Rx)
    R   = np.dot(R,Ry)
    R   = R.T
    V   = np.dot(R,a3(Target)-a3(Origin))
 
    return V
def R180(value,pi):
    value = value - abs(value)//(2*pi) * (2*pi) * math.copysign(1,value)
    value = value - int(abs(value)>pi) * (2*pi) * math.copysign(1,value)
    return value
def Range(value,R):
    try : 
        for i in range(len(value)):
            if abs(value[i])>R:
                value[i] = math.copysign(R,value[i])
    except :
        if abs(value)>R:
            value = math.copysign(R,value)
    return value
def curve1(x):
    s = x*x*x*5e5
 
    return Range(s,1)
def curve2(x):
    s = x/40
    return Range(s,1)
def curve3(x):
    s = abs(x)**0.25*math.copysign(1,x)
    return Range(s,1)
def pos(v):
    if v>0: return v
    else  : return 0
def larg(v,l):
    if abs(v)<l: v=math.copysign(l,v)
    return v
def mnofst(v,l):
    v=larg(v,l)
    v=v-math.copysign(l,v)
    return v
def d3(A,B=[0,0,0]):
    A,B = a3(A),a3(B)
    return math.sqrt((A[0]-B[0])**2+(A[1]-B[1])**2+(A[2]-B[2])**2)
def ve3(A):
    V=v3()
    V.X,V.Y,V.Z=A[0],A[1],A[2]
    return V
 
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])
 
    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]
 
    div = det(xdiff, ydiff)
 
    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y
 
def local_nor(L,a,i):
    L=a3(L)
    def local2D(x,y,ang): 
        _x = x*math.sin(ang) + y*math.cos(ang)
        _y = x*math.cos(ang) - y*math.sin(ang)
        return _x,_y
    xe,ye = local2D(L[0],L[1],-a)
    ze,ye = local2D(ye,L[2],-i)
    return xe,ye,ze
 
def predict_ball(Location,Velocity,Spin,time):
    gravity = 650
    ball_radius = 93
    max_ball_speed = 6000
    bounce_multiplier = 0.6
    air_resistance = 0.03
    surface_friction = 230
    side_wall = 4100
    backboard = 5140
    ceiling = 2050
    floor = 0
    goal_width = 900
    goal_height = 645
    Location,Velocity,Spin = a3(Location),a3(Velocity),a3(Spin)
    predicted_location = np.array([0,0,0])
 
    predicted_location = Location + Velocity*time
    predicted_velocity = Velocity
 
    # # # Bounces :
    if abs(predicted_location[0]) + ball_radius > side_wall and predicted_location[2]>200 :
        predicted_location[0] = RangeBounce(predicted_location[0],bounce_multiplier,ball_radius,side_wall)
        predicted_velocity[0] *= -bounce_multiplier
        angle_xy = math.atan2(abs(Velocity[0]),abs(Velocity[1]))/math.pi
        predicted_velocity[1] *=0.77
        predicted_velocity[2] *=0.77
    if abs(predicted_location[1]) + ball_radius > backboard and predicted_location[2]>200 and (abs(predicted_location[0])>goal_width or abs(predicted_location[2])>goal_height) :
        predicted_location[1] = RangeBounce(predicted_location[1],bounce_multiplier,ball_radius,backboard)
        predicted_velocity[1] *= -bounce_multiplier
        predicted_velocity[0] *=0.77
        predicted_velocity[2] *=0.77
    if predicted_location[2] + ball_radius > ceiling or predicted_location[2] - ball_radius - 1 < floor :
        predicted_location[2] = RangeBounce(predicted_location[2],bounce_multiplier,ball_radius,ceiling)
        predicted_velocity[2] *= -bounce_multiplier
        predicted_velocity[0] *=0.77
        predicted_velocity[1] *=0.77
        if predicted_location[2] -ball_radius < floor: predicted_location[2] = -(predicted_location[2]-ball_radius)*0.6 + ball_radius
        predicted_velocity[2] *= -bounce_multiplier
 
    if Location[2]>ball_radius+1 :
        # Gravity
        if abs(predicted_velocity[2])>0.1 : # if not floating
            predicted_velocity[2] -= gravity*time
    else :
        # Sliding Friction
        for i in range(2):
            if abs(predicted_velocity[i])>565:
                predicted_velocity[i] -= 230*math.copysign(1,predicted_velocity[i])
 
    # Air Resistance
    predicted_velocity *= (1-air_resistance*time)
 
    
     # restricting abs Velocity to less than the maximum ball speed :
    predicted_velocity = Range(predicted_velocity,max_ball_speed)
    return predicted_location, predicted_velocity
def RangeBounce(value,multiplier,radius,R):
    value += math.copysign(radius,value)
    if abs(value)>R:
        value = math.copysign(R - abs(R-abs(value))*multiplier,value)
    value -= math.copysign(radius,value)
    return value
 
gravity = 655
ball_radius = 92.8
max_ball_speed = 6000
bounce_multiplier = 0.6
air_resistance = 0.03072
surface_friction = 230
side_wall = 4100
back_wall = 5140
ceiling = 2055
floor = 0
goal_width = 910
goal_height = 645
 
def _collision(Location,Velocity,excdim=3):
    global ball_radius,side_wall,back_wall,ceiling,floor,goal_width,goal_height
    
    c=[]
    c.append([predict_z_impact(Location[2],Velocity[2],ball_radius),ball_radius,2])
    c.append([predict_z_impact(Location[2],Velocity[2],ceiling-ball_radius),ceiling-ball_radius,2])
    c.append([predict_xy_impact(Location[0],Velocity[0],side_wall-ball_radius),side_wall-ball_radius,0])
    c.append([predict_xy_impact(Location[0],Velocity[0],-side_wall+ball_radius),-side_wall+ball_radius,0])
    c.append([predict_xy_impact(Location[1],Velocity[1],back_wall-ball_radius),back_wall-ball_radius,1])
    c.append([predict_xy_impact(Location[1],Velocity[1],-back_wall+ball_radius),-back_wall+ball_radius,1])
 
    for i in range(len(c)):
        if i == 0:
            for _ in range(len(c)):
                if c[_][0]!=excdim:
                    impact_time = c[_][0]
                    impact_point = c[_][1]
                    idim = c[_][2]
                    break
 
        if c[i][0]>0 and c[i][0]<impact_time and c[i][0]!=excdim :
            impact_time = c[i][0]
            impact_point = c[i][1]
            idim = c[i][2]
 
    return impact_time,impact_point,idim
def predict_equation(Location,Velocity,time):
    global ball_radius,max_ball_speed,bounce_multiplier,air_resistance,surface_friction,side_wall,back_wall,ceiling,floor,goal_width,goal_height
 
    gravity = 655
    time=time+0.0075*time
    g = np.array([0,0,1])
 
    if d3(Velocity,[0,0,0])==0 : 
        gravity = 0
 
    for i in range(30):
 
        impact_time, impact_point, idim = _collision(Location,Velocity)
 
        ## Bounces 
        if impact_time<time and time!=0  and impact_time>=0 :
    
            impact_location = Location + (Velocity*(1-air_resistance*impact_time*(0.35)) - 0.5*gravity*impact_time*g)*impact_time
            impact_velocity = Velocity*(1-air_resistance*impact_time) - 0.5*gravity*impact_time*g
 
            if not at_goal(impact_location):
                
                time = time - impact_time
 
                impact_velocity[idim] *= -0.6
 
                if abs(impact_velocity[idim])>25:
                    impact_velocity[(idim+1)%3] *= 0.725
                    impact_velocity[(idim-1)%3] *= 0.725
 
                Location = impact_location
                Velocity = impact_velocity
 
                if abs(Velocity[2])<2 and Location[2]<ball_radius+1: 
                    gravity=0
                    Location[2]=ball_radius
                    Velocity[2]=0
                    break
 
                if time>=5e-3:
                    Location = Location + (Velocity*(1-air_resistance*5e-3*(0.35)) - (0.5)*gravity*5e-3*g)*5e-3
                    Velocity = Velocity*(1-air_resistance*5e-3) - gravity*5e-3*g
                    time-=5e-3
            else:
                break
        else:
            break
 
 
    predicted_location = Location + (Velocity*(1-(10*air_resistance**2)*time) - (0.5)*gravity*time*g)*time
    predicted_velocity = (Velocity - gravity*time*g)*(1-air_resistance*time)
 
    # freezing the ball on goal line
    if at_goal(predicted_location): 
        impact_time+=0.06
        predicted_location = Location + (Velocity*(1-air_resistance*impact_time*(0.35)) - (0.5)*gravity*impact_time*g)*impact_time
        predicted_velocity = Velocity - gravity*impact_time*gravity
 
    return predicted_location, predicted_velocity
def predict_car(Location,Velocity,time):
    gravity = 625
    ball_radius = 93
    max_ball_speed = 6000
    aires = 0.03
    surface_friction = 230
    side_wall = 4100
    back_wall = 5140
    ceiling = 2055
    bmult = 0.01
    cmult = 0.5
    car_height = 17
    goal_width = 900
    goal_height = 645
 
    g = np.array([0,0,1])
    Location,Velocity=a3(Location),a3(Velocity)
 
    _location = Location + (Velocity*(1-aires*time*(0.35)) - (0.5)*gravity*time*g)*time
    _velocity = Velocity*(1-aires*time) - gravity*time*g
 
    if _location[2]<car_height:
        i_time = predict_z_impact(Location[2],Velocity[2],car_height)
        im_location = Location + (Velocity*(1-aires*i_time*(0.35)) - (0.5)*gravity*i_time*g)*i_time
        im_velocity = Velocity*(1-aires*i_time) - gravity*i_time*g
        _location = (0.1*_location + im_location*0.9)
        _velocity = _velocity*0.1
        _location[2]=car_height
        _velocity[2]=0
    if abs(_location[0])>side_wall:
        i_time = predict_xy_impact(Location[0],Velocity[0],math.copysign(side_wall-car_height,_location[0]))
        im_location = Location + (Velocity*(1-aires*i_time*(0.35)) - (0.5)*gravity*i_time*g)*i_time
        im_velocity = Velocity*(1-aires*i_time) - gravity*i_time*g
        _location[0]=math.copysign(side_wall-car_height,_location[0])
        _velocity[0]=0
        _location[1] = (0.4*_location[1] + im_location[1]*0.6)
        _velocity[1] = _velocity[1]*0.2
    if abs(_location[1])>back_wall and (abs(_location[0])>goal_width or _location[2]>goal_height):
        i_time = predict_xy_impact(Location[1],Velocity[1],math.copysign(back_wall-car_height,_location[1]))
        im_location = Location + (Velocity*(1-aires*i_time*(0.35)) - (0.5)*gravity*i_time*g)*i_time
        im_velocity = Velocity*(1-aires*i_time) - gravity*i_time*g
        _location[1]=math.copysign(back_wall-car_height,_location[1])
        _velocity[1]=0
        _location[0] = (0.4*_location[0] + im_location[0]*0.6)
        _velocity[0] = _velocity[0]*0.2
        
 
    return _location,_velocity
def predict_z_impact(Location,Velocity,impact_point):
    gravity = 650
    bounce_multiplier = 0.6
    air_resistance = 0.03
 
    a = (.35*Velocity*air_resistance  + .5*gravity)
    b = -Velocity
    c = (-Location+impact_point)
 
    if  a!=0 and b*b -4*a*c >=0:
        t1 = (-b + math.sqrt(b*b -4*a*c))/(2*a)
        t2 = (-b - math.sqrt(b*b -4*a*c))/(2*a)
        t = t1
        if t2<t1 and t2>=0: t = t2
    else:
        t = 0
 
    return t
def predict_xy_impact(Location,Velocity,impact_point):
    air_resistance = 0.03
 
    a = (.35*Velocity*air_resistance)
    b = -Velocity
    c = (-Location+impact_point)
 
    if  a!=0 and b*b -4*a*c >=0:
        t1 = (-b + math.sqrt(b*b -4*a*c))/(2*a)
        t2 = (-b - math.sqrt(b*b -4*a*c))/(2*a)
        t = t1
        if t2<t1 and t2>=0: t = t2
    else:
        t = 0
 
    return t
def at_goal(impact_location):
    global goal_width,goal_height,back_wall
    return (abs(impact_location[0])<=goal_width-40 and impact_location[2]<=goal_height-55 and abs(impact_location[1])>back_wall-94)
def on_wall(Location):
    Location = a3(Location) 
    return (( abs(Location[0]) > 4000-75  or  abs(Location[1]) > 5000-75 or ( abs(Location[0]) > 2900-60 and abs(Location[1]) > 4000-60)) or Location[2] > 1800) and abs(Location[1]<5150 and abs(Location[0]) <4150)
 
 
wx,wy,wz=side_wall,back_wall,ceiling
dodge,jump = 0,0
airtime,gtime,djtime,jcount,lpoG,lJ,llJ=0,0,0,0,0,0,0
_c=0
_tt=0
 
def Strat():
    global t,c,Index,pB,ball,tL,pL,d,ga,od,aiming,oz,oy,ox,od,oa,oi,oL,gx,gy,gz,tgd,gd,ga,gi,ogx,ogy,ogz,ogd,oga,ogi,goal,owngoal,nx,ny,nz,nd,na,ni,bH,gxaim,gzaim
 
    c = -(player.Team-0.5)*2
    aiming = False
 
    opIndex = -1
 
    for i in range(Game.numCars):
        if i!=Index and Game.gamecars[i].Team!=player.Team and (opIndex==-1 or d3(Game.gamecars[i].Location,tL)<d3(Game.gamecars[opIndex].Location,tL))  :
            opIndex=i
 
    opp = Game.gamecars[opIndex]
 
    if Bra71L==True and player.Score.Goals + opp.Score.OwnGoals - opp.Score.Goals - player.Score.OwnGoals>5:
        c*=-1
        if _c%60==1 and verbose>0:print('Bra7iL',player.Score.Goals + opp.Score.OwnGoals - opp.Score.Goals - player.Score.OwnGoals)
    
 
    goal = np.array([-Range(t.L.X*.6,500),5250*c,Range(tL[2],250)])
    owngoal = np.array([0,-5350*c,93])
    
    gx,gy,gz = local(goal,pL,pR)
    gd,ga,gi = spherical(gx,gy,gz)
    tgd = d3(t.L,goal)
 
    ogx,ogy,ogz = local(owngoal,pL,pR)
    ogd,oga,ogi = spherical(ogx,ogy,ogz)
 
    oL = opp.Location
    ox,oy,oz = local(oL,t.L,pR)
    od,oa,oi = spherical(ox,oy,oz)
 
    nx,ny,nz=local(t.L,pL,pR)
    nd,na,ni = spherical(nx,ny,nz)
    
    bH=Game.gameInfo.bBallHasBeenHit 
    if  bH :
        ChaseBall()
    else:
        KickoffChase()
 
    pL = a3(pL)
    tLV = tL + tV * ( .5*abs(ny) + 0.9*abs(nx) + .35*abs(nz))/1500
    gxaim = line_intersection(([-800,goal[1]], [800,goal[1]]), ([pL[0],pL[1]], [tLV[0],tLV[1]]))[0]
    gzaim = line_intersection(([-250,goal[1]], [250,goal[1]]), ([pL[2],pL[1]], [tLV[2],tLV[1]]))[0]
    pL = ve3(pL)
    
 
    if (c*tL[1]>4700) and abs(tL[0])>1300 or (abs(tL[0]>3900 and abs(a-oga)<0.3 )) or (d3(owngoal,pL)+40> d3(owngoal,tL) and od<d and abs(R180(oga-a,1))>0.2):
        GoTo((owngoal*0.08+tL*0.92))
        if _c%7==1 and verbose>0:print("retreating",_c)
 
 
solved=False 
ctime=0
__vd=1
__tV=[1,1,1]
na,ga,oga=0,0,0
 
def KickoffChase():
 
    global t,ball,pL,pV,tL,tV,taV,dist,dist2,d2,z,a,poG,pB,Index,Game,time,c,_c,ga,od,poG,aiming,bH
    
    t = Target(ball)
    aiming = False
    tL,tV,taV = a3(t.L),a3(t.V),a3(t.aV)
    dist2=math.sqrt((t.L.X-pL.X)**2+(t.L.Y-pL.Y)**2)
    dist=d3(t.L,pL)
 
    oL = Game.gamecars[1-Index].Location
    oV = Game.gamecars[1-Index].Velocity
    od = d3(a3(oL)+a3(oV)/15,tL)
    opd = d3(a3(oL)+a3(oV)/15,pL)
 
    if od <900 or bH:
        pL = a3(pL)  + a3(pV)*(Range((dist)/(2500+((not poG)*1100)),1/4))
        pL = ve3(pL)
 
    #curves
    d = d3(tL,pL)
    d2 =math.sqrt((x)**2+(y)**2)
 
    #Bias
    if abs(pL.X)>1000 or True:
        # tL[1] += Range(pL.Y,350)/8
        tL[0] -= Range(pL.X,1000)/(5+ (not poG)*5)
 
    if abs(pL.X)>800: pB=3
    elif not poG and abs(a)<0.05 and d<1400: pB = 0
# 
def ChaseBall():
 
    global U,t,ball,pL,pV,tL,tV,taV,dist,dist2,d2,z,a,poG,pB,Index,Game,time,c,_c,na,ga,oga,poG,aiming,_z,_vd,_tvd,_pvd,_tva,_pva,_vi,_t,oz,oy,ox,od,oa,oi,goal,owngoal,vx,vy,vz,_tt
    
    t = Target(ball)
    tL,tV,taV = a3(t.L),a3(t.V),a3(t.aV)
 
    aiming=pL.Y*c>-5280
 
    if abs(pV.Z)<9: pV.Z=0
    dist2=math.sqrt((t.L.X-pL.X)**2+(t.L.Y-pL.Y)**2)
    dist=d3(tL,pL)
 
    lL=tL-a3(pL)
    az=math.atan2(lL[1],lL[0])
    ni=math.atan2(lL[2],dist2)
 
    tvx,tvy,tvz = local_nor(tV,az,ni)
    pvx,pvy,pvz = local_nor(pV,az,ni)
    vx,vy,vz = local_nor(tV-a3(pV),az,ni)
 
    vd=d3([vx,vy,vz])
 
    _pt = dist/larg(abs(pvy),2000)
    # _tt = pos(dist)/larg(d3([vy,vz,vx]),abs(d3([0.5*tvx,tvy,tvz]))+0.8*abs(d3([pvx,pvy,pvz]))+1e-4)
    _tt = ((pos(nd+pos(vx)/5+pos(vz)/5)/2300 + ( .6*abs(ny) + 0.8*abs(nx) + .34*abs(nz))/1450)/2 * 0.7 + 0.3*pos(dist)/larg(d3([vy,vz,vx]),abs(d3([0.5*tvx,tvy,tvz]))+0.8*abs(d3([pvx,pvy,pvz]))+1e-4))
    # _tt = pos(_tt + dist/58000)
 
    if _tt<30 : # Prediction Stuff
        
        tL,tV = predict_equation(tL,tV,_tt)
        # tL = tL + tV*(_tt)
 
        impact_time, impact_point, idim = _collision(tL,tV,2)
        impact_time-=1/7
        if tL[2]>480 and not on_wall(tL) and impact_time>0 :
            tL = tL + (tV*(1-0.037*impact_time*(0.35)) - 0.5*655*impact_time*np.array([0,0,1]))*impact_time
            if _c%7==1  and verbose>0 : print("sfdw")
 
        # if not on_wall(pL) and not poG and pL.Z>160 :
        #   time = Range(_t,0.5+(dist)/3000)
        #   gravity = 250*np.array([0,0,1])*((pL.Z+pV.Z*time)>0 or True)
        #   # tL = tL  - (a3(pV)-gravity*time)*time
        #   tL - a3(pV)*_t
        # else:
        #   tL = tL  - a3(pV)*(Range(_t,1/8)) 
 
        # pL,_ = predict_car(a3(pL),a3(pV),_t)
        # pL = ve3(pL)
 
        # tL = tL  + a3(t.V)/50
        pV=a3(pV)
        if not poG and (pL.Z>400): 
            pL = a3(pL) + (pV*(1-0.0307*0.35*_tt) - (not poG)*325*_tt*np.array([0,0,1]) )*(_tt)
            if pL[2]<15: pL[2]=15
 
        pL = a3(pL)  + a3(pV)/900
        pL = ve3(pL)
        pV = ve3(pV)
 
    #curves
    d = d3(tL,pL)
    d2=math.sqrt((nx)**2+(ny)**2)
 
    #get down from the wall
    if pL.Z>50 and poG and on_wall(pL) and (t.L.Z<z or z> 650 +pB*14):
        tL[2]=0 
 
def Aim():
    global x,y,z
    
    if d3(owngoal,pL)> d3(owngoal,tL) or (abs(R180(oga-a,1))<0.2 and abs(oga)<0.25) : 
        wa = R180(ga-0.5*math.copysign(1,t.L.X),1)
        if abs(R180(oga-a,1))<0.15 : 
            # if abs(t.L.X)<1400: wa = R180(ga+0.5*math.copysign(1,x),1)
            # if abs(x)<90 : wa = R180(ga-0.75*math.copysign(1,x),1)
            x = x -math.copysign(105,wa) -Range(Range(wa*95,95)*(pos(d2-170)/300),abs(ga*150))
        else: x = x -Range(-Range(ga*95,95)*(pos(d2-300)/600),abs(ga*105))*(nz<250)*poG - math.copysign(104,oga)
        y = y+Range(ogy,30)
        z = z+Range(ogz,20)
    
    # elif ogd>500:
    else:
        wa = R180(R180(ga-a,1)+R180(_a/50,1),1)
 
        x = x + Range(wa*(5),1)*120*(abs(wa)>0.015)*(1-(nz>90)*larg(abs(z),360)/720 )*math.copysign(1,y)  + Range(curve3(mnofst(wa,0.05))*mnofst(y-_y*0.7*_tt,299),599)*(nz<150)*poG/2*(abs(gxaim)>300)
        y = y-Range(gy,9+(z>140)*40)
        # z = z-Range(gz,25)
 
def ChaseCar(index):
    global t,ball,pL,pV,tL,tV,taV,dist,dist2,z,a,poG,pB,Index,Game,time,c,_c,_vd
 
    if _c%10==1:print('bumping')
    t = Target(Game.gamecars[index])
 
    tL,tV,taV = a3(t.L),a3(t.V),a3(t.aV)
    dist=d3(t.L,pL)
    dist2=math.sqrt((t.L.X-pL.X)**2+(t.L.Y-pL.Y)**2)
 
    timesteps = 1
    for i in range(timesteps):
        tL,tV = predict_ball(tL,tV,taV,(dist-40)/larg(_vd,1)/timesteps)
 
    
    tL =  tL  - a3(pV)*(Range((dist-40)/larg(_vd,1),1/15)) 
 
    if pL.Z>50 and poG and (t.L.Z<z or z> 650 +pB*14):
        tL[2]=0
Bi=0
def GetBoost(Bi):
    global t,Game,tL,tV,dist,dist2,time,pL,od,pV,na,aiming
    # Bi=0 # 28, 29 side boosts, 30,33 orange corner , 31,32 blue corner
    Bd,i=0,Bi
    while i <34:
        if Bd==0 or (d3(Game.gameBoosts[i].Location,a3(pL)+a3(pV)/3)<Bd and Game.gameBoosts[i].bActive):
            Bi=i
            Bd=d3(Game.gameBoosts[i].Location,a3(pL)+a3(pV)/3)
        i+=1
    # if Bi>33: Bi=0
    t = Target(Game.gameBoosts[Bi])
    aiming=False
    tL,tV = a3(t.L),a3(t.V)
    dist=d3(t.L,pL)
    dist2=math.sqrt((t.L.X-pL.X)**2+(t.L.Y-pL.Y)**2)
    tL =  tL  - a3(pV)*1/30
    tL[2]=0
 
    nx,ny,nz=local(t.L,pL,pR)
    nd,na,ni = spherical(nx,ny,nz)
 
def GoTo(point):
    global t,Game,tL,tV,dist,dist2,Bi,time,pL,od
    t = Target([point])
    aiming=False
    tL,tV = a3(t.L),a3(t.V)
    dist=d3(t.L,pL)
    dist2=math.sqrt((t.L.X-pL.X)**2+(t.L.Y-pL.Y)**2)
    tL =  tL  - a3(pV)*1/30
    tL[2]=1
 
def roll():
    global pL,pV,pR,poG,wx,U
    r = pR.Roll/32768
    if not poG and pL.Z>150:
        if abs(pL.X+pV.X/1.5)>wx*0.95 and abs(pR.Yaw)>U/8:
            r=R180(pR.Roll-math.copysign(U/2,pR.Yaw*pL.X),U)
        if abs(pL.Y+pV.Y/1.5)>wy*0.95 and abs(U-abs(pR.Yaw))>U/8  and (abs(pL.X)>900 or abs(pL.Z)>645) :
            r=R180(pR.Roll-math.copysign(U/2,-R180(pR.Yaw+U/2,U)*pL.Y),U)
        if pL.Z+pV.Z/1.5>wz*0.95:
            r = math.copysign(U-abs(pR.Roll),-pR.Roll)
    return r
 
def AIR():
    global A,I,R,a,i,r,_a,_i,_r,poG,P,_c,jcount
    
    r=roll()
    if player.Location.Z+pV.Z/11<200 and pV.Z<-200:
        i = pR.Pitch/U +0.1*math.copysign(1,-(jcount>0) )
    P=0
    if poG: 
        if abs(a)<.5: A=curve1(a-_a/66)
        else: A=curve1(math.copysign(1-abs(a),a)+_a/66)
    else: A=math.copysign(1,a-_a/12)
    I = math.copysign(1,-i-_i/15)
    R = math.copysign(1,-r+_r/22)
 
    if abs(0.5-abs(a))>0.4 and abs(0.5-abs(i))>0.15 and abs(r)>0.01 and not poG :
        if RLBot_Version==4:
            A,P=R,1
    else: R=0
 
    _c+=1
 
def Thr():
    global T,B,P,a,x,y,_x,_y,_py,_a,A,pL,poG,dist,dist2,pB,poG,_tvd,d2
 
    xa,ya,za = x,y,z
 
    m=(abs(_y))/2300
    if 40<z<145: m = -4
    ya,xa = y -Range(_py/2.65,750)/(2-m), x -Range(_px/2.65,750)/(2-m)
    da,aa,ia = spherical(xa,ya,za)
 
    T=math.copysign(1,0.5-abs(aa))
 
    if poG :
 
        if 100<abs(x)<400 and abs(y)<200 and 0.35<abs(aa)<0.65 and aiming and abs(_py)<550 and abs(_y)<550:
            T*=-1
            A*=-1
        
        if d2>400 and abs(aa+_a/2.25)>0.45 : 
            if abs(a)>0.98: A=1
            if d2>700 and  _py<-90 :
                if abs(aa)<0.98 and abs(_a)>0.5 : P=1
                A*=-1   
            elif d2>900 and abs(a)<0.95 and _py<1000:
                T=1
 
        if T*_py>0 and 0.2<abs(aa-_a/37)<0.8 and abs(_x)<400 and _a*aa>=0:
            P=1
 
    # pB=0
    # T*=curve2((math.sqrt(x*x+y*y))*2)
    B=abs(a)<0.15 and T>0 and _py < 2290 and (dist2>140 or not poG) and (abs(0.5-abs(ni+_i/44))>0.25 or (pL.Z<25 and _y<0)) and pB>0.1
 
def Jump():
    global poG,lpoG,pdJ,lJ,llJ,pJ,player,Game,pB,time,airtime,gtime,dodge,jump,djtime,jcount,J,d,a,i,r,x,y,z,_a,A,I,R,pL,d,_py,_y,_z,_tz,_pz,t,T,dist2,_va,_vi,oga,ga,gi,_vd,_tva,_t,dist,nd,aiming,_tt
 
    if not poG and lpoG: airtime=time
    if poG and not lpoG: gtime=time
    if poG: jcount=2
    elif pdJ or (time-airtime>1.25 and pJ)  :jcount=0
    else: jcount=1
    if poG : 
        dodge = 0
        jump = 0
    J=0
 
    ti = (dist)/larg(_vd,1)
 
 
    # if poG and d<580 and 100<nz<200 and abs(R180(R180(ga-a,1)-R180(ga-na,1),1))<0.08 and abs(i-gi)>0.05 and abs(R180(_pva-na,1))<0.25 and d<270 and abs(na)<0.1 :
    #   J=1
    #   if _c%2==1:print("jumpshot",_c)
 
    # if 140<z<300+200*poG +pB*12 and z/800<_tt<z/30 and jcount>0 and time-gtime>0.05 and abs(R180(R180(ga-a,1)-R180(ga-na,1),1))<0.08 and abs(R180(i-gi,1))>0.08 and abs(R180(R180(_pva-a,1)-R180(_pva-na,1),1))<0.05 and d2<500:
    #   if _c%5==1: print('jumpy')
    #   jump=1
 
    # print((time-airtime)*(1-poG)*(pV.Z>0),pL.Z)   
 
    if jcount>0 and player.Location.Z+pV.Z/20<32 and abs(r)<0.12 and abs(a)<0.07 and y>400 and -0.02<abs(pR.Pitch/U)<0.12 and not poG and pV.Z<-200 :
        J=1
        I = abs(a)*2 -1
        A = 0
        R=0
        if verbose>0: print("wavedash")
 
    # if (not aiming) and (nd+d)/2<350 and abs(z)<180 and (abs(R180(R180(_pva-na,1)-R180(a-ga,1),1))<0.12 and abs(R180(oga-a,1))>0.2 or not aiming) and dist>100 and dist<870 and abs(x)<220 and abs(_py)>250 and abs(z+_z/15)<110 and abs(t.L.Z-pL.Z)<140 and jcount>0 and abs(pR.Pitch/U)<0.5 and tL[2]>20 and (abs(ga)<0.1 and abs(na)<0.1 or (abs(a)>0.8 and abs(oga-a)>0.2) ):
    #   dodge=1
    #   print("dodgejump")
    #   if not poG: I = abs(a)*2 -1
 
    if (not aiming) and (nd+d)/2<350 and abs(z)<180 and abs(x)<220 and abs(_py)>250 and abs(z)<110 and abs(t.L.Z-pL.Z)<140 and jcount>0 and tL[2]>20 :
        dodge=1
        if verbose>0 : print("dodgejump")
        if not poG: I = abs(a)*2 -1
 
    if jump==1 and jcount>0:
        if (z>0 and poG) or (z+_z/10>90 and not poG)  : 
            J=1
        if 0.18<time-airtime<0.2 and z>120: J=0
        if lJ!=J or llJ!=lJ: A,I,R = 0,0,0
 
    Dodge()
 
    if nd>450 and 750<(y-_y/5)<2000 and abs(na)<0.06 and abs(i)<0.1 and pL.Z<20 and poG and pB<8 and 1050<_py<1400 and time-gtime>0.2:
        J=1
        if verbose>0 :print("jump wavedash")
 
    lpoG = poG  
    llJ=lJ
    lJ=J
 
def Dodge():
 
    global poG,lpoG,pdJ,lJ,llJ,pJ,player,Game,pB,time,airtime,gtime,dodge,jump,djtime,jcount,J,d,na,nd,a,i,r,z,_a,A,I,R,pL,_py,_y,t,tL,T,d2,dist2,dist,_c,_tva,ga,oa,bH
 
 
    if dist>400 and abs(R180(_pva-a,1))<0.25 and abs(0.5-abs(a))>0.4 and time-gtime>0.1 and ((_py>1640 and _py*T>0 and (y-_y/4>3500) and pB<80 and player.bSuperSonic==0) or (abs(na)>0.75 and abs(y-_y/4)>850 and _py<-140) or (_py>1120 and _py*T>0 and ((y-_y/4>3000)) and pB<16) or (2000>_py>970 and _py*T>=0 and ((y-_y/4>2100)) and pB<4)): 
        if verbose>0: print('fliping',(y-_y/4,y))
        dodge = 1
 
    if (not bH ) and (abs(R180(oga-a,1))>0.2) and nd<230 and dist<870 and abs(x)<200 and not poG and abs(_py)>250 and abs(z+_z/15)<95 and abs(t.L.Z-pL.Z)<110 and jcount>0 and abs(pR.Pitch/U)<0.5 and tL[2]>20:
        dodge=1
        if verbose>0: print("dodging")
 
    if (dist<250 or d<100) and abs(z)<120 and  abs(R180(_pva-a,1))<0.5 and (abs(ga)<0.04 and abs(na)<0.04 or ( abs(a)>0.8 or (abs(gxaim)<300 and abs(gzaim)<999 and abs(R180(ga-a,1))<0.5 ) )  and abs(R180(oga-a,1))>0.2)  :
        J=_c%2
        I = abs(a)*2 -1
        A = (abs(R180(a+0.5,1)*2) -1)
        R = 0
        # dodge = 1
        if _c%7==1 and verbose>0: print('pushing')
 
    if dodge and 0.02<time-airtime<0.04:
        I = -(abs(a)*2 -1)
    
    if dodge==1 and jcount>0 and time-gtime>0.05:
        if 0.05<time-airtime<0.07 and not poG: 
            J=0
        else : 
            J=1
        if time-airtime> 0.09 and pL.Z>45:
            J=_c%2
            I = abs(a)*2 -1
            A = (abs(R180((na+na)/2+0.5,1)*2) -1)*0.9
            R = 0
            djtime=time
 
        if lJ!=J or llJ!=lJ:
            I = abs(a)*2 -1
            A = (abs(R180((na+na)/2+0.5,1)*2) -1)*0.9
            R = 0
            djtime=time
 
    if 0.05<time-djtime<0.25 :
        I,A,R=math.copysign(1,_i),0,0
    if 0.65>time-djtime>0.25 :
        if abs(a)<0.5 :
            if abs(a)<0.8: I = math.copysign(1,-_i)
        else: I,A,R=0,0,0
 
import math
import random
 
        
        self.force_eval = False
        
        # Dropshot
        if agent.dropshot:
            
            dir_y = sign(my_goal.location.y)
            
            self.def_pos_1 = Vec3(sign(packet.game_ball.physics.location.x) * -1000, packet.game_ball.physics.location.y + dir_y * 2000, 0.0)
            self.def_pos_2 = Make_Vect(packet.game_ball.physics.location) + Vec3(0, dir_y * 2000, 0) * 3500
            if sign(dir_y) == sign(packet.game_ball.physics.location.y):
                self.aim_pos = Make_Vect(packet.game_ball.physics.location) + Vec3(0, dir_y * 1000, 1000)
            else:
                self.aim_pos = Make_Vect(packet.game_ball.physics.location) + Vec3(0, dir_y * 1000, -1000)
            self.aggro = True
            
        # 3v3
        else:
            
            ball = Get_Ball_At_T(packet, agent.get_ball_prediction_struct(), 3)
            a = ball.location.y - my_goal.location.y
            b = ball.location.y - opponent_goal.location.y
            
            # Defensive positioning
            if abs(a) < 4000 or (abs(b) > 4000 and (ball.velocity.y + sign(my_goal.direction.y) * 1000) * sign(my_goal.direction.y) < 0.0):
                self.def_pos_2 = Vec3(sign(packet.game_ball.physics.location.x) * -3300, my_goal.location.y + my_goal.direction.y * 1000, 0.0)
                self.def_pos_1 = Make_Vect(my_goal.location).flatten() - Vec3(sign(packet.game_ball.physics.location.x) * 200, 0, 0) - Make_Vect(my_goal.direction) * 200
                if (packet.game_ball.physics.location.y - my_car.physics.location.y) * sign(my_goal.direction.y) > 0.0 or abs(packet.game_ball.physics.location.y) > 4000 or sign(my_goal.direction.y) == sign(packet.game_ball.physics.location.y):
                    self.aim_pos = Vec3(sign(packet.game_ball.physics.location.x) * 3600, packet.game_ball.physics.location.y + my_goal.direction.y * 1000, 500.0)
                else:
                    self.aim_pos = Vec3(sign(packet.game_ball.physics.location.x) * 3600, packet.game_ball.physics.location.y - my_goal.direction.y * 1000, 500.0)
                self.aggro = False
            # Offensive positioning
            else:
                self.def_pos_1 = Vec3(sign(packet.game_ball.physics.location.x) * -100, packet.game_ball.physics.location.y + opponent_goal.direction.y * 2000, 0.0)
                b_p = Make_Vect(packet.game_ball.physics.location)
                b_p.x *= 0.5
                self.def_pos_2 = b_p + Make_Vect(opponent_goal.direction) * 4000
                if (packet.game_ball.physics.location.y - my_car.physics.location.y) * sign(my_goal.direction.y) > 0.0:
                    self.aim_pos = Make_Vect(opponent_goal.location) + Vec3(0, 0, -1000)
                else:
                    self.aim_pos = Vec3(sign(packet.game_ball.physics.location.x) * 3600, packet.game_ball.physics.location.y + my_goal.direction.y * 1000, 500.0)
                self.aggro = True
        
        team = self.get_team_cars(packet)
        
        if len(team) < 1: 
            self.def_pos = self.def_pos_1
        else:
            other_car_index = 0
            
            if self.attacking_car == team[0]:
                other_car_index = 1
            
            if len(team) <= other_car_index:
                self.def_pos = self.def_pos_1
            else:
                
                c1 = packet.game_cars[agent.index].physics.location
                c2 = packet.game_cars[team[other_car_index]].physics.location
                
                l1 = (self.def_pos_1 - c1).len() * (2 - packet.game_cars[agent.index].boost * 0.01) # + (self.def_pos_2 - c2).len()
                l2 = (self.def_pos_1 - c2).len() * (2 - packet.game_cars[team[other_car_index]].boost * 0.01) # + (self.def_pos_2 - c1).len()
                
                if l1 < l2:
                    self.def_pos = self.def_pos_1
                else:
                    self.def_pos = self.def_pos_2
                
            
        
        self.pause_eval = self.pause_eval - agent.delta
        self.was_kickoff = self.kickoff
        
        # render_star(agent, self.def_pos_1, agent.renderer.blue())
        # render_star(agent, self.def_pos_2, agent.renderer.blue())
        
        # render_star(agent, Make_Vect(packet.game_cars[self.attacking_car].physics.location), agent.renderer.red())
        
        # print(dot(self.attack_car_vel, self.attack_car_to_ball))
        
        # if self.attacking_car == agent.index:
            # render_star(agent, Make_Vect(packet.game_cars[agent.index].physics.location), agent.renderer.red())
        # else:
            # render_star(agent, Make_Vect(packet.game_cars[agent.index].physics.location), agent.renderer.blue())
        
        # if len(team) > 0:
            # agent.renderer.draw_line_3d(packet.game_cars[agent.index].physics.location, packet.game_cars[team[0]].physics.location, agent.renderer.purple())
        
        # if len(team) > 1:
            # agent.renderer.draw_line_3d(packet.game_cars[agent.index].physics.location, packet.game_cars[team[1]].physics.location, agent.renderer.purple())
    
 
from rlbot.agents.base_agent import BaseAgent
from rlbot.utils.structures.quick_chats import QuickChats
 
 
def get_game_score(packet: GameTickPacket):
    score = [0, 0]  # Index 0 is team0, index 1 is team1
 
    for car in packet.game_cars:
        score[car.team] += car.score_info.goals
 
    return score
 
 
class QuickChatExampleAgent(BaseAgent):
    def initialize_agent():
        self.previous_frame_opponent_score = 0
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        controller = SimpleControllerState()
 
        current_score = get_game_score(packet)
        if self.previous_frame_opponent_score < current_score[not self.team]:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_NiceShot)
 
        self.previous_frame_opponent_score = current_score[not self.team]
 
        return controller
 
    def handle_quick_chat(self, index, team, quick_chat):
        if team != self.team and quick_chat == QuickChats.Compliments_NiceShot:
            self.send_quick_chat(QuickChats.CHAT_EVERYONE, QuickChats.Compliments_Thanks)
            class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
 
        # Contants
        self.DODGE_TIME = 0.2
        self.DISTANCE_TO_DODGE = 500
        self.DISTANCE_FROM_BALL_TO_BOOST = 1500  # The minimum distance the ball needs to be away from the bot for the bot to boost
        # The angle (from the front of the bot to the ball) at which the bot should start to powerslide.
        self.POWERSLIDE_ANGLE = math.radians(170)
 
        # Game values
        self.bot_pos = None
        self.bot_yaw = None
 
        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0
 
    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)
 
        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw
 
        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi
 
        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0
 
        self.controller.handbrake = abs(math.degrees(angle_front_to_target)) < self.POWERSLIDE_ANGLE
 
    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1
 
            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location
 
        # Boost when ball is far enough away
        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST
 
        # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        self.controller.throttle = 1
 
        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)
 
        # Boost on kickoff
        if ball_pos.x == 0 and ball_pos.x == 0:
            self.aim(ball_pos.x, ball_pos.x)
            self.controller.boost = True
 
        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0
 
        self.check_for_dodge()
 
        return self.controller
        class diabloBot(BaseAgent):
    def __init__(self, name, team, index):
        Game.set_mode("soccar")
        self.game = Game(index, team)
        self.index = index
        self.name = name
        self.team = team
 
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.me = physicsObject()
        self.ball = physicsObject()
        self.me.team = self.team
        self.allies = []
        self.enemies = []
        self.start = 5
        self.flipStart = 0
        self.flipping = False
        self.controller = None
        self.flipTimer = time.time()
        self.activeState = Kickoff(self)
        self.gameInfo = None
        self.onSurface = False
        self.boosts = []
        self.fieldInfo = []
        self.positions = []
        self.time = 0
        self.deltaTime = 0
        self.maxSpd = 2200
        self.ballPred = []
        self.selectedBallPred = None
        self.ballDelay = 0
        self.renderCalls = []
        self.ballPredObj = None
        self.carHeight = 84
        self.forward = True
        self.velAngle = 0
        self.onWall = False
        self.stateTimer = time.time()
        self.contested = True
        self.flipTimer = time.time()
        self.goalPred = None
 
    def getActiveState(self):
        if type(self.activeState) == JumpingState:
            return 0
        if type(self.activeState) == Kickoff:
            return 1
        if type(self.activeState) == GetBoost:
            return 2
        if type(self.activeState) == Dribble:
            return 3
        if type(self.activeState) == GroundShot:
            return 4
        if type(self.activeState) == GroundDefend:
            return 5
        if type(self.activeState) == halfFlip:
            return 6
 
    def setHalfFlip(self):
        self.activeState = halfFlip(self)
 
    def determineFacing(self):
        offset = self.me.location + self.me.velocity
        loc = toLocal(offset,self.me)
        angle = math.degrees(math.atan2(loc[1],loc[0]))
        if angle < -180:
            angle += 360
        if angle > 180:
            angle -= 360
 
        if abs(angle) >150 and self.getCurrentSpd() > 200:
            self.forward = False
        else:
            self.forward = True
 
        self.velAngle = angle
 
 
 
    def setJumping(self,targetType):
        _time = time.time()
        if _time - self.flipTimer > 2:
            if self.me.location[2] > 250:
                self.activeState = JumpingState(self, -1)
            else:
                self.activeState = JumpingState(self, targetType)
            self.flipTimer = _time
 
    def setDashing(self,target):
        self.activeState = WaveDashing(self,target)
 
 
    def getCurrentSpd(self):
        return Vector(self.me.velocity[:2]).magnitude()
 
    def updateSelectedBallPrediction(self,ballStruct):
        x = physicsObject()
        x.location = Vector([ballStruct.physics.location.x, ballStruct.physics.location.y, ballStruct.physics.location.z])
        x.velocity = Vector([ballStruct.physics.velocity.x, ballStruct.physics.velocity.y, ballStruct.physics.velocity.z])
        x.rotation = Vector([ballStruct.physics.rotation.pitch, ballStruct.physics.rotation.yaw, ballStruct.physics.rotation.roll])
        x.avelocity = Vector([ballStruct.physics.angular_velocity.x, ballStruct.physics.angular_velocity.y, ballStruct.physics.angular_velocity.z])
        x.local_location = localizeVector(x.location, self.me)
        self.ballPredObj = x
 
 
 
 
    def preprocess(self, game):
        self.ballPred = self.get_ball_prediction_struct()
        self.players = [self.index]
        self.game.read_game_information(game,
                                        self.get_rigid_body_tick(),
                                        self.get_field_info())
        car = game.game_cars[self.index]
        self.me.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
        self.me.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
        self.me.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
        self.me.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
        self.me.boostLevel = car.boost
        self.onSurface = car.has_wheel_contact
        self.deltaTime = clamp(1/60,1/300,self.game.time_delta)
 
 
        ball = game.game_ball.physics
        self.ball.location = Vector([ball.location.x, ball.location.y, ball.location.z])
        self.ball.velocity = Vector([ball.velocity.x, ball.velocity.y, ball.velocity.z])
        self.ball.rotation = Vector([ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll])
        self.ball.avelocity = Vector([ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z])
        self.me.matrix = rotator_to_matrix(self.me)
        self.ball.local_location = localizeVector(self.ball.location,self.me)
        self.determineFacing()
        self.onWall = False
        if self.onSurface:
            if self.me.location[2] > 70:
                self.onWall = True
 
        self.allies.clear()
        self.enemies.clear()
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                _obj = physicsObject()
                _obj.index = i
                _obj.team = car.team
                _obj.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
                _obj.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
                _obj.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
                _obj.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
                _obj.boostLevel = car.boost
                _obj.local_location = localizeVector(_obj,self.me)
 
                if car.team == self.team:
                    self.allies.append(_obj)
                else:
                    self.enemies.append(_obj)
        self.gameInfo = game.game_info
        self.boosts.clear()
        self.fieldInfo = self.get_field_info()
        for index in range(len(self.fieldInfo.boost_pads)):
            packetBoost = game.game_boosts[index]
            fieldInfoBoost = self.fieldInfo.boost_pads[index]
            self.boosts.append(Boost_obj([fieldInfoBoost.location.x,fieldInfoBoost.location.y,fieldInfoBoost.location.z],fieldInfoBoost.is_full_boost, packetBoost.is_active))
 
        ballContested(self)
        self.goalPred = None
 
 
 
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        if len(self.allies) >=1:
            teamStateManager(self)
        else:
            soloStateManager(self)
        action = self.activeState.update()
 
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(100, 100, 1, 1, str(type(self.activeState)), self.renderer.white())
 
        for each in self.renderCalls:
            each.run()
        self.renderer.end_rendering()
        self.renderCalls.clear()
 
        return action
    
 
 
class TutorialBot(BaseAgent):
    def __init__(self, name, team, index):
        super().__init__(name, team, index)
        self.controller = SimpleControllerState()
 
        # Contants
        self.DODGE_TIME = 0.2
        self.DISTANCE_TO_DODGE = 500
        self.DISTANCE_FROM_BALL_TO_BOOST = 1500  # The minimum distance the ball needs to be away from the bot for the bot to boost
        # The angle (from the front of the bot to the ball) at which the bot should start to powerslide.
        self.POWERSLIDE_ANGLE = math.radians(170)
 
        # Game values
        self.bot_pos = None
        self.bot_yaw = None
 
        # Dodging
        self.should_dodge = False
        self.on_second_jump = False
        self.next_dodge_time = 0
 
    def aim(self, target_x, target_y):
        angle_between_bot_and_target = math.atan2(target_y - self.bot_pos.y,
                                                target_x - self.bot_pos.x)
 
        angle_front_to_target = angle_between_bot_and_target - self.bot_yaw
 
        # Correct the values
        if angle_front_to_target < -math.pi:
            angle_front_to_target += 2 * math.pi
        if angle_front_to_target > math.pi:
            angle_front_to_target -= 2 * math.pi
 
        if angle_front_to_target < math.radians(-10):
            # If the target is more than 10 degrees right from the centre, steer left
            self.controller.steer = -1
        elif angle_front_to_target > math.radians(10):
            # If the target is more than 10 degrees left from the centre, steer right
            self.controller.steer = 1
        else:
            # If the target is less than 10 degrees from the centre, steer straight
            self.controller.steer = 0
 
        self.controller.handbrake = abs(math.degrees(angle_front_to_target)) < self.POWERSLIDE_ANGLE
 
    def check_for_dodge(self):
        if self.should_dodge and time.time() > self.next_dodge_time:
            self.controller.jump = True
            self.controller.pitch = -1
 
            if self.on_second_jump:
                self.on_second_jump = False
                self.should_dodge = False
            else:
                self.on_second_jump = True
                self.next_dodge_time = time.time() + self.DODGE_TIME
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        # Update game data variables
        self.bot_yaw = packet.game_cars[self.team].physics.rotation.yaw
        self.bot_pos = packet.game_cars[self.index].physics.location
        ball_pos = packet.game_ball.physics.location
 
        # Boost when ball is far enough away
        self.controller.boost = distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) > self.DISTANCE_FROM_BALL_TO_BOOST
 
        # Blue has their goal at -5000 (Y axis) and orange has their goal at 5000 (Y axis). This means that:
        # - Blue is behind the ball if the ball's Y axis is greater than blue's Y axis
        # - Orange is behind the ball if the ball's Y axis is smaller than orange's Y axis
        self.controller.throttle = 1
 
        if (self.index == 0 and self.bot_pos.y < ball_pos.y) or (self.index == 1 and self.bot_pos.y > ball_pos.y):
            self.aim(ball_pos.x, ball_pos.y)
            if distance(self.bot_pos.x, self.bot_pos.y, ball_pos.x, ball_pos.y) < self.DISTANCE_TO_DODGE:
                self.should_dodge = True
        else:
            if self.team == 0:
                # Blue team's goal is located at (0, -5000)
                self.aim(0, -5000)
            else:
                # Orange team's goal is located at (0, 5000)
                self.aim(0, 5000)
 
        # Boost on kickoff
        if ball_pos.x == 0 and ball_pos.x == 0:
            self.aim(ball_pos.x, ball_pos.x)
            self.controller.boost = True
 
        # This sets self.jump to be active for only 1 frame
        self.controller.jump = 0
 
        self.check_for_dodge()
 
        return self.controller
        class diabloBot(BaseAgent):
    def __init__(self, name, team, index):
        Game.set_mode("soccar")
        self.game = Game(index, team)
        self.index = index
        self.name = name
        self.team = team
 
    def initialize_agent(self):
        self.controller_state = SimpleControllerState()
        self.me = physicsObject()
        self.ball = physicsObject()
        self.me.team = self.team
        self.allies = []
        self.enemies = []
        self.start = 5
        self.flipStart = 0
        self.flipping = False
        self.controller = None
        self.flipTimer = time.time()
        self.activeState = Kickoff(self)
        self.gameInfo = None
        self.onSurface = False
        self.boosts = []
        self.fieldInfo = []
        self.positions = []
        self.time = 0
        self.deltaTime = 0
        self.maxSpd = 2200
        self.ballPred = []
        self.selectedBallPred = None
        self.ballDelay = 0
        self.renderCalls = []
        self.ballPredObj = None
        self.carHeight = 84
        self.forward = True
        self.velAngle = 0
        self.onWall = False
        self.stateTimer = time.time()
        self.contested = True
        self.flipTimer = time.time()
        self.goalPred = None
 
    def getActiveState(self):
        if type(self.activeState) == JumpingState:
            return 0
        if type(self.activeState) == Kickoff:
            return 1
        if type(self.activeState) == GetBoost:
            return 2
        if type(self.activeState) == Dribble:
            return 3
        if type(self.activeState) == GroundShot:
            return 4
        if type(self.activeState) == GroundDefend:
            return 5
        if type(self.activeState) == halfFlip:
            return 6
 
    def setHalfFlip(self):
        self.activeState = halfFlip(self)
 
    def determineFacing(self):
        offset = self.me.location + self.me.velocity
        loc = toLocal(offset,self.me)
        angle = math.degrees(math.atan2(loc[1],loc[0]))
        if angle < -180:
            angle += 360
        if angle > 180:
            angle -= 360
 
        if abs(angle) >150 and self.getCurrentSpd() > 200:
            self.forward = False
        else:
            self.forward = True
 
        self.velAngle = angle
 
 
 
    def setJumping(self,targetType):
        _time = time.time()
        if _time - self.flipTimer > 2:
            if self.me.location[2] > 250:
                self.activeState = JumpingState(self, -1)
            else:
                self.activeState = JumpingState(self, targetType)
            self.flipTimer = _time
 
    def setDashing(self,target):
        self.activeState = WaveDashing(self,target)
 
 
    def getCurrentSpd(self):
        return Vector(self.me.velocity[:2]).magnitude()
 
    def updateSelectedBallPrediction(self,ballStruct):
        x = physicsObject()
        x.location = Vector([ballStruct.physics.location.x, ballStruct.physics.location.y, ballStruct.physics.location.z])
        x.velocity = Vector([ballStruct.physics.velocity.x, ballStruct.physics.velocity.y, ballStruct.physics.velocity.z])
        x.rotation = Vector([ballStruct.physics.rotation.pitch, ballStruct.physics.rotation.yaw, ballStruct.physics.rotation.roll])
        x.avelocity = Vector([ballStruct.physics.angular_velocity.x, ballStruct.physics.angular_velocity.y, ballStruct.physics.angular_velocity.z])
        x.local_location = localizeVector(x.location, self.me)
        self.ballPredObj = x
 
 
 
 
    def preprocess(self, game):
        self.ballPred = self.get_ball_prediction_struct()
        self.players = [self.index]
        self.game.read_game_information(game,
                                        self.get_rigid_body_tick(),
                                        self.get_field_info())
        car = game.game_cars[self.index]
        self.me.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
        self.me.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
        self.me.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
        self.me.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
        self.me.boostLevel = car.boost
        self.onSurface = car.has_wheel_contact
        self.deltaTime = clamp(1/60,1/300,self.game.time_delta)
 
 
        ball = game.game_ball.physics
        self.ball.location = Vector([ball.location.x, ball.location.y, ball.location.z])
        self.ball.velocity = Vector([ball.velocity.x, ball.velocity.y, ball.velocity.z])
        self.ball.rotation = Vector([ball.rotation.pitch, ball.rotation.yaw, ball.rotation.roll])
        self.ball.avelocity = Vector([ball.angular_velocity.x, ball.angular_velocity.y, ball.angular_velocity.z])
        self.me.matrix = rotator_to_matrix(self.me)
        self.ball.local_location = localizeVector(self.ball.location,self.me)
        self.determineFacing()
        self.onWall = False
        if self.onSurface:
            if self.me.location[2] > 70:
                self.onWall = True
 
        self.allies.clear()
        self.enemies.clear()
        for i in range(game.num_cars):
            if i != self.index:
                car = game.game_cars[i]
                _obj = physicsObject()
                _obj.index = i
                _obj.team = car.team
                _obj.location = Vector([car.physics.location.x, car.physics.location.y, car.physics.location.z])
                _obj.velocity = Vector([car.physics.velocity.x, car.physics.velocity.y, car.physics.velocity.z])
                _obj.rotation = Vector([car.physics.rotation.pitch, car.physics.rotation.yaw, car.physics.rotation.roll])
                _obj.avelocity = Vector([car.physics.angular_velocity.x, car.physics.angular_velocity.y, car.physics.angular_velocity.z])
                _obj.boostLevel = car.boost
                _obj.local_location = localizeVector(_obj,self.me)
 
                if car.team == self.team:
                    self.allies.append(_obj)
                else:
                    self.enemies.append(_obj)
        self.gameInfo = game.game_info
        self.boosts.clear()
        self.fieldInfo = self.get_field_info()
        for index in range(len(self.fieldInfo.boost_pads)):
            packetBoost = game.game_boosts[index]
            fieldInfoBoost = self.fieldInfo.boost_pads[index]
            self.boosts.append(Boost_obj([fieldInfoBoost.location.x,fieldInfoBoost.location.y,fieldInfoBoost.location.z],fieldInfoBoost.is_full_boost, packetBoost.is_active))
 
        ballContested(self)
        self.goalPred = None
 
 
 
 
    def get_output(self, packet: GameTickPacket) -> SimpleControllerState:
        self.preprocess(packet)
        if len(self.allies) >=1:
            teamStateManager(self)
        else:
            soloStateManager(self)
        action = self.activeState.update()
 
        self.renderer.begin_rendering()
        self.renderer.draw_string_2d(100, 100, 1, 1, str(type(self.activeState)), self.renderer.white())
 
        for each in self.renderCalls:
            each.run()
        self.renderer.end_rendering()
        self.renderCalls.clear()
 
        return action
