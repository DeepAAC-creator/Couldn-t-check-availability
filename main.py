from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

def set_window():
    if sys.platform != 'darwin':
        import pywintypes
        import win32gui
        import win32com.client
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        win32gui.SetForegroundWindow(pygame.display.get_wm_info()['window'])
#student_code_starts
#Song: Sky High x Feel Good Mashup
#Music provided by NoCopyrightSounds
#Free Download/Stream: http://ncs.io/SHxFG
#Watch: http://ncs.lnk.to/SHxFGAT/youtube
import sys, pygame, random, time, csv, math

name = input('请输入你的姓名: ')

pygame.init()  # pygame 初始化
f_clock = pygame.time.Clock()  # 创建时钟对象
screen = pygame.display.set_mode((800, 600))  # 创建屏幕
set_window() # 定位窗口
bg = pygame.image.load('pic/bg.png')
player = pygame.image.load('pic/主角.png')
fire = pygame.image.load('pic/火焰.png')
button = pygame.image.load('pic/开始按钮.png')
board = pygame.image.load('pic/榜单.png')
button_rect = button.get_rect()
button_rect.x = 300
button_rect.y = 250
FPS = 60  # 设置游戏刷新率
player_rect = player.get_rect()
player_rect.center = (400, 300)  # 初始位置设为窗口中心
font = pygame.font.Font('font/字体3.ttf', 32)
game = 'ready'
auto_play = True  # 添加自动游玩开关
# 设置背景音乐
pygame.mixer.music.load("music/Elektronomia, Syn Cole - Sky High x Feel Good Mashup [NCS Release].mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(loops=-1)

names = []
nums = []
try:
    with open("排行榜.csv", "r") as f:
        text = csv.reader(f)
        for row in text:
            if row:
                names.append(row[0])
                nums.append(float(row[1]))
except FileNotFoundError:
    # 如果排行榜文件不存在，创建默认排行榜
    names = ["玩家1", "玩家2", "玩家3", "玩家4", "玩家5"]
    nums = [50.0, 40.0, 30.0, 20.0, 10.0]  # 从高到低排列
    with open("排行榜.csv", "w", newline="") as f:
        writer = csv.writer(f)
        for i in range(len(names)):
            writer.writerow([names[i], nums[i]])

# 确保排行榜有足够的条目并按从高到低排列
while len(names) < 5:
    names.append("玩家" + str(len(names) + 1))
    nums.append(60.0 - len(names) * 10)  # 确保新添加的分数更低

# 对排行榜进行排序（从高到低）
def sort_leaderboard():
    global nums, names
    # 将分数和名字配对并排序
    combined = list(zip(nums, names))
    combined.sort(reverse=True)  # 从高到低排序
    nums, names = zip(*combined)
    nums = list(nums)
    names = list(names)

# 初始排序
sort_leaderboard()

# 显示排行榜
def show(list1, list2):
    screen.blit(board, (100, 50))
    
    # 显示前5名（从高到低）
    for i in range(min(5, len(list1))):
        if list2[i] == name:
            color = (60, 179, 113)  # 绿色突出显示当前玩家
        else:
            color = (61, 89, 171)   # 蓝色其他玩家
        
        # 显示排名、名字和分数
        rank_text = font.render(f"{i+1}.", True, color)
        name_text = font.render(list2[i], True, color)
        score_text = font.render(f"{list1[i]:.2f}", True, color)
        
        screen.blit(rank_text, (230, 160 + i * 50))
        screen.blit(name_text, (280, 160 + i * 50))
        screen.blit(score_text, (500, 160 + i * 50))

# 存储排行榜
def save(nums, names):
    with open('排行榜.csv', 'w', newline='') as f:
        csvfile = csv.writer(f)
        for i in range(len(nums)):
            csvfile.writerow([names[i], nums[i]])

class Ball:
    def __init__(self, pos, color):
        self.pos = pos
        self.color = color
        self.direction = 'left'
        self.speed_x = random.choice([-4, 4])
        self.speed_y = random.choice([-4, 4])
        self.radius = 20  # 添加半径属性用于碰撞检测

    def show(self):
        self.pos[0] += self.speed_x
        self.pos[1] += self.speed_y
        if self.pos[0] > 780 or self.pos[0] < 20:
            self.speed_x = - self.speed_x
        if self.pos[1] > 580 or self.pos[1] < 20:
            self.speed_y = - self.speed_y
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def change_speed(self, speed):
        if self.speed_x > 0:
            self.speed_x = speed
        else:
            self.speed_x = -speed
        if self.speed_y > 0:
            self.speed_y = speed
        else:
            self.speed_y = -speed

# 改进的自动控制AI - 精确预测和直接躲避
class AIController:
    def __init__(self):
        self.smooth_factor = 0.3  # 平滑移动因子
        self.emergency_threshold = 80  # 紧急避障阈值
        self.safe_threshold = 150  # 安全距离阈值
        self.random_move_timer = 0
        self.random_direction = [0, 0]
        self.prediction_time = 1.0  # 预测时间（秒）
    
    def predict_ball_trajectory(self, ball, player_pos, max_time=2.0, steps=20):
        """精确预测球的轨迹，考虑边界反弹"""
        trajectory = []
        current_pos = ball.pos.copy()
        current_speed_x = ball.speed_x
        current_speed_y = ball.speed_y
        
        dt = max_time / steps
        
        for i in range(steps):
            # 更新位置
            current_pos[0] += current_speed_x * dt
            current_pos[1] += current_speed_y * dt
            
            # 检查边界碰撞
            bounced = False
            if current_pos[0] > 780:
                current_pos[0] = 780 - (current_pos[0] - 780)
                current_speed_x = -current_speed_x
                bounced = True
            elif current_pos[0] < 20:
                current_pos[0] = 20 + (20 - current_pos[0])
                current_speed_x = -current_speed_x
                bounced = True
                
            if current_pos[1] > 580:
                current_pos[1] = 580 - (current_pos[1] - 580)
                current_speed_y = -current_speed_y
                bounced = True
            elif current_pos[1] < 20:
                current_pos[1] = 20 + (20 - current_pos[1])
                current_speed_y = -current_speed_y
                bounced = True
            
            trajectory.append(current_pos.copy())
            
            # 如果反弹了，可能需要调整预测
            if bounced:
                # 简化处理：反弹后重新计算轨迹
                pass
                
        return trajectory
    
    def find_best_escape_direction(self, player_pos, ball_trajectory, player_radius=25, ball_radius=20):
        """找到最佳的逃离方向，避免与球的轨迹相交"""
        safe_directions = []
        danger_time = None
        
        # 检查轨迹中每个点与玩家的距离
        for i, pos in enumerate(ball_trajectory):
            dx = pos[0] - player_pos[0]
            dy = pos[1] - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # 如果距离小于安全阈值，计算危险时间
            if distance < player_radius + ball_radius + 10:  # 加上一些缓冲
                danger_time = i * (self.prediction_time / len(ball_trajectory))
                break
        
        # 如果没有危险，返回None
        if danger_time is None:
            return None
        
        # 计算球的危险位置
        danger_pos = ball_trajectory[min(len(ball_trajectory)-1, int(danger_time * len(ball_trajectory) / self.prediction_time))]
        
        # 计算从玩家到危险位置的向量
        danger_vec = [danger_pos[0] - player_pos[0], danger_pos[1] - player_pos[1]]
        danger_dist = math.sqrt(danger_vec[0]**2 + danger_vec[1]**2)
        
        if danger_dist > 0:
            danger_vec[0] /= danger_dist
            danger_vec[1] /= danger_dist
        
        # 计算垂直于危险方向的逃离方向（左右两个方向）
        escape_dir1 = [-danger_vec[1], danger_vec[0]]  # 顺时针旋转90度
        escape_dir2 = [danger_vec[1], -danger_vec[0]]  # 逆时针旋转90度
        
        # 选择远离屏幕中心的方向（避免被逼到角落）
        center_x, center_y = 400, 300
        to_center1 = [center_x - (player_pos[0] + escape_dir1[0]*50), 
                     center_y - (player_pos[1] + escape_dir1[1]*50)]
        to_center2 = [center_x - (player_pos[0] + escape_dir2[0]*50), 
                     center_y - (player_pos[1] + escape_dir2[1]*50)]
        
        dist1 = math.sqrt(to_center1[0]**2 + to_center1[1]**2)
        dist2 = math.sqrt(to_center2[0]**2 + to_center2[1]**2)
        
        # 选择更靠近中心的方向
        if dist1 < dist2:
            return escape_dir1
        else:
            return escape_dir2
    
    def calculate_immediate_threat(self, player_pos, balls):
        """计算即时威胁（最近的球）"""
        closest_ball = None
        min_distance = float('inf')
        threat_direction = [0, 0]
        
        for ball in balls:
            dx = ball.pos[0] - player_pos[0]
            dy = ball.pos[1] - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < min_distance:
                min_distance = distance
                closest_ball = ball
                if distance > 0:
                    threat_direction = [dx/distance, dy/distance]
        
        return closest_ball, min_distance, threat_direction
    
    def avoid_borders(self, player_pos, screen_width, screen_height):
        """避免靠近屏幕边界"""
        border_buffer = 50
        border_force = [0, 0]
        
        # 左边界
        if player_pos[0] < border_buffer:
            border_force[0] += (border_buffer - player_pos[0]) / border_buffer
        # 右边界
        if player_pos[0] > screen_width - border_buffer:
            border_force[0] -= (player_pos[0] - (screen_width - border_buffer)) / border_buffer
        # 上边界
        if player_pos[1] < border_buffer:
            border_force[1] += (border_buffer - player_pos[1]) / border_buffer
        # 下边界
        if player_pos[1] > screen_height - border_buffer:
            border_force[1] -= (player_pos[1] - (screen_height - border_buffer)) / border_buffer
        
        # 归一化
        magnitude = math.sqrt(border_force[0]**2 + border_force[1]**2)
        if magnitude > 0:
            border_force[0] /= magnitude
            border_force[1] /= magnitude
            
        return border_force
    
    def is_safe(self, player_pos, balls):
        """检查当前位置是否安全"""
        for ball in balls:
            dx = ball.pos[0] - player_pos[0]
            dy = ball.pos[1] - player_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < self.safe_threshold:
                return False
                
        return True
    
    def get_random_direction(self):
        """生成随机方向"""
        angle = random.uniform(0, 2 * math.pi)
        return [math.cos(angle), math.sin(angle)]
    
    def get_move_direction(self, player_pos, balls, screen_width, screen_height):
        # 检查是否安全，如果安全则进行随机移动
        if self.is_safe(player_pos, balls):
            self.random_move_timer += 1
            
            # 每45帧改变一次随机方向
            if self.random_move_timer > 45:
                self.random_direction = self.get_random_direction()
                self.random_move_timer = 0
                
            # 结合边界避障
            border_force = self.avoid_borders(player_pos, screen_width, screen_height)
            move_x = self.random_direction[0] * 0.7 + border_force[0] * 0.3
            move_y = self.random_direction[1] * 0.7 + border_force[1] * 0.3
            
            # 归一化
            magnitude = math.sqrt(move_x*move_x + move_y*move_y)
            if magnitude > 0:
                move_x /= magnitude
                move_y /= magnitude
                
            return [move_x * 4, move_y * 4]
        
        # 如果不安全，使用精确预测躲避算法
        self.random_move_timer = 0
        
        # 计算每个球的轨迹
        escape_directions = []
        weights = []
        
        for ball in balls:
            trajectory = self.predict_ball_trajectory(ball, player_pos, self.prediction_time, 20)
            escape_dir = self.find_best_escape_direction(player_pos, trajectory)
            
            if escape_dir is not None:
                # 计算威胁权重（基于距离）
                dx = ball.pos[0] - player_pos[0]
                dy = ball.pos[1] - player_pos[1]
                distance = math.sqrt(dx*dx + dy*dy)
                weight = max(0, self.emergency_threshold - distance) / self.emergency_threshold
                
                escape_directions.append(escape_dir)
                weights.append(weight)
        
        # 如果没有找到逃离方向，使用即时威胁计算
        if not escape_directions:
            closest_ball, min_distance, threat_direction = self.calculate_immediate_threat(player_pos, balls)
            if closest_ball is not None:
                # 直接逃离威胁方向
                escape_x = -threat_direction[0]
                escape_y = -threat_direction[1]
                escape_directions = [[escape_x, escape_y]]
                weights = [1.0]
        
        # 计算加权平均逃离方向
        if escape_directions:
            total_x, total_y = 0, 0
            total_weight = sum(weights)
            
            for i, (x, y) in enumerate(escape_directions):
                total_x += x * weights[i]
                total_y += y * weights[i]
            
            # 归一化
            magnitude = math.sqrt(total_x*total_x + total_y*total_y)
            if magnitude > 0:
                total_x /= magnitude
                total_y /= magnitude
            
            escape_direction = [total_x, total_y]
        else:
            escape_direction = [0, 0]
        
        # 结合边界避障
        border_force = self.avoid_borders(player_pos, screen_width, screen_height)
        move_x = escape_direction[0] * 0.8 + border_force[0] * 0.2
        move_y = escape_direction[1] * 0.8 + border_force[1] * 0.2
        
        # 归一化
        magnitude = math.sqrt(move_x*move_x + move_y*move_y)
        if magnitude > 0:
            move_x /= magnitude
            move_y /= magnitude
        
        # 根据紧急程度调整速度
        closest_ball, min_distance, _ = self.calculate_immediate_threat(player_pos, balls)
        if closest_ball is not None:
            speed_factor = 1.0 + max(0, (self.emergency_threshold - min_distance) / self.emergency_threshold) * 2.0
        else:
            speed_factor = 1.0
        
        return [move_x * 6 * speed_factor, move_y * 6 * speed_factor]

# 创建AI控制器实例
ai_controller = AIController()

# 初始化小球
a = Ball([random.randint(50, 750), random.randint(50, 550)], (255, 0, 0))
b = Ball([random.randint(50, 750), random.randint(50, 550)], (0, 0, 255))

timer = 0  # 初始化计时器
# 游戏主循环
while True:
    # 检测事件
    for event in pygame.event.get():
        # 退出游戏
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if button_rect.collidepoint(mouse_pos) and game == 'ready':
                game = 'play'
                start = time.time()  # 开始计时
                # 重置玩家位置到中心
                player_rect.center = (400, 300)
                # 重置小球位置
                a.pos = [random.randint(50, 750), random.randint(50, 550)]
                b.pos = [random.randint(50, 750), random.randint(50, 550)]
                a.speed_x = random.choice([-4, 4])
                a.speed_y = random.choice([-4, 4])
                b.speed_x = random.choice([-4, 4])
                b.speed_y = random.choice([-4, 4])
        # 添加按键切换自动/手动模式 - 修复这里
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # 检测按下A键
                auto_play = not auto_play  # 切换模式
                print(f"模式切换: {'自动' if auto_play else '手动'}")
            # 添加其他按键检测，防止按键冲突
            if event.key == pygame.K_ESCAPE:  # ESC键退出
                pygame.quit()
                sys.exit()
    
    # 绘制背景
    screen.blit(bg, (0, 0))
    
    if game == 'ready':
        screen.blit(button, button_rect)
        # 显示当前模式提示
        mode_text = font.render(f"当前模式: {'自动' if auto_play else '手动'} (按A切换)", True, (255, 255, 255))
        screen.blit(mode_text, (250, 350))

    if game == 'play':
        # 计算分值
        now = time.time()
        timer = now - start

        # 自动或手动控制玩家
        if auto_play:
            # 自动控制
            player_center = player_rect.center
            move_dir = ai_controller.get_move_direction(player_center, [a, b], 800, 600)
            new_x = player_center[0] + move_dir[0]
            new_y = player_center[1] + move_dir[1]
            
            # 确保不超出边界
            new_x = max(10, min(790, new_x))
            new_y = max(10, min(590, new_y))
            
            player_rect.center = (new_x, new_y)
        else:
            # 手动控制
            pos = pygame.mouse.get_pos()
            player_rect.center = pos
        
        screen.blit(player, player_rect)

        # 小球移动
        a.show()
        b.show()

        # 加速功能 - 随时间增加速度
        speed_increase = 4 + timer / 10
        a.change_speed(min(speed_increase, 10))  # 限制最大速度
        b.change_speed(min(speed_increase, 10))  # 限制最大速度

        # 碰撞检测 - 使用圆形碰撞检测
        player_center = player_rect.center
        player_radius = min(player_rect.width, player_rect.height) / 2
        
        # 计算玩家与球a的距离
        dx_a = player_center[0] - a.pos[0]
        dy_a = player_center[1] - a.pos[1]
        distance_a = (dx_a**2 + dy_a**2)**0.5
        
        # 计算玩家与球b的距离
        dx_b = player_center[0] - b.pos[0]
        dy_b = player_center[1] - b.pos[1]
        distance_b = (dx_b**2 + dy_b**2)**0.5
        
        # 如果距离小于两者半径之和，则发生碰撞
        if distance_a < (player_radius + a.radius) or distance_b < (player_radius + b.radius):
            game = 'over'
        
        # 边缘检测
        player_pos = player_rect.center
        if player_pos[0] < 10 or player_pos[0] > 790:
            game = 'over'
        if player_pos[1] < 10 or player_pos[1] > 590:
            game = 'over'

    if game != 'ready':
        # 显示即时分数
        score = font.render(f'{timer:.2f}', True, (255, 255, 255))
        screen.blit(score, (40, 35))
        # 显示当前模式
        mode_text = font.render("模式: " + ("自动" if auto_play else "手动") + " (按A切换)", True, (255, 255, 255))
        screen.blit(mode_text, (500, 35))
    
    # 游戏结束后
    if game == 'over':
        num = float(f'{timer:.2f}')
        # 只有当成绩比排行榜最低成绩好时才更新
        if num > nums[-1] if nums else 0:  # 如果比最后一名好
            # 添加新成绩
            nums.append(num)
            names.append(name)
            
            # 重新排序排行榜（从高到低）
            sort_leaderboard()
            
            # 如果超过5个记录，移除最差的
            if len(nums) > 5:
                nums = nums[:5]
                names = names[:5]
            
            # 保存排行榜
            save(nums, names)
        
        game = 'show'

    if game == 'show':
        show(nums, names)
        # 添加重新开始按钮
        restart_text = font.render("点击任意位置重新开始", True, (255, 255, 255))
        screen.blit(restart_text, (250, 500))
        
        # 检测点击重新开始
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed[0]:
            game = 'ready'

    f_clock.tick(FPS)
    # 更新屏幕
    pygame.display.update()
#student_code_ends