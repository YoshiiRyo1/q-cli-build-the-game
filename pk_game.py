import pygame
import sys
import random
import math
from enum import Enum

# 画面の設定
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# 色の定義 - ISS Deluxe風のカラーパレット
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (16, 148, 16)      # ISS風の芝生色
DARK_GREEN = (8, 120, 8)   # 暗い芝生色
LIGHT_GREEN = (32, 180, 32) # 明るい芝生色
RED = (232, 32, 32)       # ユニフォーム赤
BLUE = (32, 80, 232)      # ユニフォーム青
GOAL_GRAY = (192, 192, 192) # ゴールの灰色
NET_WHITE = (240, 240, 240) # ネットの白
SKIN_COLOR = (248, 184, 136) # 肌色
PLAYER_BLUE = (48, 104, 216) # プレイヤーの青
KEEPER_RED = (216, 48, 48)   # キーパーの赤
BALL_WHITE = (248, 248, 248) # ボールの白
PITCH_GREEN = (16, 148, 16)  # メインの芝生色
PITCH_DARK = (8, 120, 8)     # 暗い芝生色
PITCH_LIGHT = (32, 180, 32)  # 明るい芝生色
GOAL_POST = (224, 224, 224)  # ゴールポストの色（白っぽく）
SKY_BLUE = (96, 176, 248)    # 背景の空色
UI_BLUE = (16, 48, 144)      # UI背景の青
UI_DARK_BLUE = (8, 24, 96)   # UI背景の暗い青
GOLD = (248, 216, 96)        # 金色
YELLOW = (248, 216, 32)      # 黄色（ライン用）
SCOREBOARD_BG = (16, 16, 64) # スコアボード背景

# ゴールエリアの定義
class GoalArea(Enum):
    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 2
    MIDDLE_LEFT = 3
    MIDDLE_CENTER = 4
    MIDDLE_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTER = 7
    BOTTOM_RIGHT = 8

# ゲームの状態
class GameState(Enum):
    MENU = 0
    PLAYER_KICKING = 1
    AI_GOALKEEPING = 2
    AI_KICKING = 3
    PLAYER_GOALKEEPING = 4
    RESULT = 5

class PKGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Soccer Penalty Kick Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        
        # ゲーム変数の初期化
        self.reset_game()
    
    def reset_game(self):
        self.state = GameState.MENU
        self.round = 1
        self.player_score = 0
        self.ai_score = 0
        self.player_results = [None, None, None, None, None]  # 各ラウンドの結果 (True=ゴール, False=失敗)
        self.ai_results = [None, None, None, None, None]      # 各ラウンドの結果 (True=ゴール, False=失敗)
        self.selected_area = GoalArea.MIDDLE_CENTER
        self.ai_selected_area = None
        self.result_message = ""
        self.animation_timer = 0
        self.show_sankaku_tobi = False  # 三角飛びメッセージの表示フラグ
        self.super_save = False         # 三角飛び発動フラグ
    
    def run(self):
        running = True
        while running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                self.handle_event(event)
            
            # 状態更新
            self.update()
            
            # 描画
            self.draw()
            
            # フレームレート制御
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == GameState.MENU:
                if event.key == pygame.K_SPACE:
                    self.state = GameState.PLAYER_KICKING
            
            elif self.state == GameState.PLAYER_KICKING:
                # キッカーとしての操作
                if event.key == pygame.K_UP:
                    if self.selected_area in [GoalArea.MIDDLE_LEFT, GoalArea.MIDDLE_CENTER, GoalArea.MIDDLE_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 3)
                    elif self.selected_area in [GoalArea.BOTTOM_LEFT, GoalArea.BOTTOM_CENTER, GoalArea.BOTTOM_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 3)
                elif event.key == pygame.K_DOWN:
                    if self.selected_area in [GoalArea.TOP_LEFT, GoalArea.TOP_CENTER, GoalArea.TOP_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value + 3)
                    elif self.selected_area in [GoalArea.MIDDLE_LEFT, GoalArea.MIDDLE_CENTER, GoalArea.MIDDLE_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value + 3)
                elif event.key == pygame.K_LEFT:
                    if self.selected_area in [GoalArea.TOP_CENTER, GoalArea.MIDDLE_CENTER, GoalArea.BOTTOM_CENTER]:
                        self.selected_area = GoalArea(self.selected_area.value - 1)
                    elif self.selected_area in [GoalArea.TOP_RIGHT, GoalArea.MIDDLE_RIGHT, GoalArea.BOTTOM_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 1)
                elif event.key == pygame.K_RIGHT:
                    if self.selected_area in [GoalArea.TOP_LEFT, GoalArea.MIDDLE_LEFT, GoalArea.BOTTOM_LEFT]:
                        self.selected_area = GoalArea(self.selected_area.value + 1)
                    elif self.selected_area in [GoalArea.TOP_CENTER, GoalArea.MIDDLE_CENTER, GoalArea.BOTTOM_CENTER]:
                        self.selected_area = GoalArea(self.selected_area.value + 1)
                elif event.key == pygame.K_SPACE:
                    # AIのゴールキーパーの動きを決定
                    self.ai_selected_area = GoalArea(random.randint(0, 8))
                    self.state = GameState.AI_GOALKEEPING
                    self.animation_timer = 0
            
            elif self.state == GameState.PLAYER_GOALKEEPING:
                # ゴールキーパーとしての操作
                if event.key == pygame.K_UP:
                    if self.selected_area in [GoalArea.MIDDLE_LEFT, GoalArea.MIDDLE_CENTER, GoalArea.MIDDLE_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 3)
                    elif self.selected_area in [GoalArea.BOTTOM_LEFT, GoalArea.BOTTOM_CENTER, GoalArea.BOTTOM_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 3)
                elif event.key == pygame.K_DOWN:
                    if self.selected_area in [GoalArea.TOP_LEFT, GoalArea.TOP_CENTER, GoalArea.TOP_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value + 3)
                    elif self.selected_area in [GoalArea.MIDDLE_LEFT, GoalArea.MIDDLE_CENTER, GoalArea.MIDDLE_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value + 3)
                elif event.key == pygame.K_LEFT:
                    if self.selected_area in [GoalArea.TOP_CENTER, GoalArea.MIDDLE_CENTER, GoalArea.BOTTOM_CENTER]:
                        self.selected_area = GoalArea(self.selected_area.value - 1)
                    elif self.selected_area in [GoalArea.TOP_RIGHT, GoalArea.MIDDLE_RIGHT, GoalArea.BOTTOM_RIGHT]:
                        self.selected_area = GoalArea(self.selected_area.value - 1)
                elif event.key == pygame.K_RIGHT:
                    if self.selected_area in [GoalArea.TOP_LEFT, GoalArea.MIDDLE_LEFT, GoalArea.BOTTOM_LEFT]:
                        self.selected_area = GoalArea(self.selected_area.value + 1)
                    elif self.selected_area in [GoalArea.TOP_CENTER, GoalArea.MIDDLE_CENTER, GoalArea.BOTTOM_CENTER]:
                        self.selected_area = GoalArea(self.selected_area.value + 1)
                elif event.key == pygame.K_SPACE:
                    # AIのキッカーの動きを決定
                    self.ai_selected_area = GoalArea(random.randint(0, 8))
                    self.state = GameState.AI_KICKING
                    self.animation_timer = 0
            
            elif self.state == GameState.RESULT:
                if event.key == pygame.K_SPACE:
                    self.reset_game()
    
    def update(self):
        if self.state == GameState.AI_GOALKEEPING:
            # キック直後に三角飛び判定を行う
            if self.animation_timer == 0:
                # 10%の確率で必ずセーブする特殊能力
                self.super_save = random.random() < 0.1
                
                # 特殊能力が発動した場合、キーパーの位置をキッカーが選んだ位置に強制移動
                if self.super_save and self.selected_area != self.ai_selected_area:
                    self.ai_selected_area = self.selected_area
                    self.show_sankaku_tobi = True
                else:
                    self.show_sankaku_tobi = False
            
            self.animation_timer += 1
            if self.animation_timer > 60:  # 1秒間のアニメーション
                # 判定結果を適用
                if hasattr(self, 'super_save') and self.super_save and self.show_sankaku_tobi:
                    # 三角飛び発動時は必ずセーブ
                    self.result_message = "SAVED!"
                    self.player_results[self.round - 1] = False  # 失敗を記録
                else:
                    # 通常の判定
                    if self.selected_area == self.ai_selected_area:
                        # セーブ
                        self.result_message = "SAVED!"
                        self.player_results[self.round - 1] = False  # 失敗を記録
                    else:
                        # ゴール
                        self.player_score += 1
                        self.result_message = "GOAL!"
                        self.player_results[self.round - 1] = True  # 成功を記録
                
                # 次のフェーズへ
                self.animation_timer = 0
                self.state = GameState.PLAYER_GOALKEEPING
                self.selected_area = GoalArea.MIDDLE_CENTER
        
        elif self.state == GameState.AI_KICKING:
            self.animation_timer += 1
            if self.animation_timer > 60:  # 1秒間のアニメーション
                # 10%の確率で必ずセーブする特殊能力
                super_save = random.random() < 0.1
                
                # キック直後に三角飛び判定を行う
                if self.animation_timer == 0:
                    # 10%の確率で必ずセーブする特殊能力
                    self.super_save = random.random() < 0.1
                    
                    # 特殊能力が発動した場合、キーパーの位置をキッカーが選んだ位置に強制移動
                    if self.super_save and self.selected_area != self.ai_selected_area:
                        self.selected_area = self.ai_selected_area
                        self.show_sankaku_tobi = True
                    else:
                        self.show_sankaku_tobi = False
                
                if self.animation_timer > 60:  # 1秒間のアニメーション
                    # 判定結果を適用
                    if hasattr(self, 'super_save') and self.super_save and self.show_sankaku_tobi:
                        # 三角飛び発動時は必ずセーブ
                        self.result_message = "NICE SAVE!"
                        self.ai_results[self.round - 1] = False  # AIの失敗を記録
                    else:
                        # 通常の判定
                        if self.selected_area == self.ai_selected_area:
                            # セーブ
                            self.result_message = "NICE SAVE!"
                            self.ai_results[self.round - 1] = False  # AIの失敗を記録
                        else:
                            # ゴール
                            self.ai_score += 1
                            self.result_message = "GOAL CONCEDED!"
                            self.ai_results[self.round - 1] = True  # AIの成功を記録
                
                # 次のラウンドへ
                self.animation_timer = 0
                self.round += 1
                
                if self.round > 5:
                    self.result_message = ""  # 結果メッセージをクリア
                    self.state = GameState.RESULT
                else:
                    self.state = GameState.PLAYER_KICKING
                    self.selected_area = GoalArea.MIDDLE_CENTER
    
    def draw(self):
        # 背景は各ビュー関数内で描画するため、ここではクリアしない
        
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state in [GameState.PLAYER_KICKING, GameState.AI_GOALKEEPING]:
            self.draw_kicking_view()
        elif self.state in [GameState.PLAYER_GOALKEEPING, GameState.AI_KICKING]:
            self.draw_goalkeeping_view()
        elif self.state == GameState.RESULT:
            self.draw_result()
        
        # メニュー画面以外でスコアボードを表示
        if self.state != GameState.MENU and self.state != GameState.RESULT:
            # ISS風のスコアボード
            score_panel_width = 300
            score_panel_height = 60
            
            # スコアボードの背景（黒）
            pygame.draw.rect(self.screen, BLACK, (10, 10, score_panel_width, score_panel_height))
            pygame.draw.rect(self.screen, WHITE, (10, 10, score_panel_width, score_panel_height), 1)
            
            # ISS風のチーム表示
            team_font = pygame.font.SysFont(None, 30)
            player_text = team_font.render("PLAYER", True, WHITE)
            ai_text = team_font.render("AI", True, WHITE)  # CPUからAIに変更
            
            # テキスト配置は各結果表示部分で行うため、ここでは削除
            
            # 結果マーク表示（アルファベット）
            result_font = pygame.font.SysFont(None, 28)
            circle = "O"  # ゴール成功
            cross = "X"   # ゴール失敗
            
            # プレイヤーの結果表示 - 1行目
            self.screen.blit(player_text, (20, 15))
            for i in range(5):
                x_pos = 20 + player_text.get_width() + 10 + i * 25
                if i < self.round:
                    if self.player_results[i] == True:
                        result_mark = result_font.render(circle, True, GREEN)
                    elif self.player_results[i] == False:
                        result_mark = result_font.render(cross, True, RED)
                    else:
                        continue  # 結果がまだない場合はスキップ
                    self.screen.blit(result_mark, (x_pos, 15))
            
            # AIの結果表示 - 2行目
            self.screen.blit(ai_text, (20, 40))
            for i in range(5):
                x_pos = 20 + player_text.get_width() + 10 + i * 25
                if i < self.round:
                    if self.ai_results[i] == True:
                        result_mark = result_font.render(circle, True, GREEN)
                    elif self.ai_results[i] == False:
                        result_mark = result_font.render(cross, True, RED)
                    else:
                        continue  # 結果がまだない場合はスキップ
                    self.screen.blit(result_mark, (x_pos, 40))
            
            # ラウンド表示は不要
        
        # 結果メッセージを表示（ゴールやセーブの結果）
        if self.result_message and self.state != GameState.MENU:
            # ISS風のメッセージボックス
            message_width = 300
            message_height = 60
            message_x = SCREEN_WIDTH // 2 - message_width // 2
            message_y = 80
            
            # メッセージの背景（黒）
            pygame.draw.rect(self.screen, BLACK, (message_x, message_y, message_width, message_height))
            
            # メッセージの枠（色分け）
            if "GOAL" in self.result_message:
                border_color = BLUE  # ゴール時は青
            else:
                border_color = RED   # セーブ時は赤
            
            pygame.draw.rect(self.screen, border_color, (message_x, message_y, message_width, message_height), 2)
            
            # 結果メッセージ（ISS風の点滅効果）
            blink_rate = (pygame.time.get_ticks() % 400) / 400.0
            if blink_rate > 0.5:
                message_color = YELLOW
            else:
                message_color = WHITE
            
            result_text = self.font.render(self.result_message, True, message_color)
            self.screen.blit(result_text, (message_x + message_width // 2 - result_text.get_width() // 2, 
                                         message_y + message_height // 2 - result_text.get_height() // 2))
            
            # ISS風のアクションアイコン
            icon_size = 40
            if "GOAL" in self.result_message:
                # ゴールアイコン（ボール）
                pygame.draw.circle(self.screen, WHITE, (message_x - 30, message_y + message_height // 2), icon_size // 2)
                pygame.draw.circle(self.screen, BLACK, (message_x - 30, message_y + message_height // 2), icon_size // 2, 1)
            else:
                # セーブアイコン（グローブ）- プレイヤーの色に合わせて青色に
                pygame.draw.circle(self.screen, PLAYER_BLUE, (message_x - 30, message_y + message_height // 2), icon_size // 2)
                pygame.draw.circle(self.screen, WHITE, (message_x - 30, message_y + message_height // 2), icon_size // 2, 2)
        
        # 三角飛びメッセージは各ビューで表示するため、ここでは削除
        
        pygame.display.flip()
    
    def draw_menu(self):
        # フィールドを描画（背景として）
        self.draw_field()
        
        # ゴールを描画（装飾として）
        goal_width = 400
        goal_height = 200
        goal_x = SCREEN_WIDTH // 2 - goal_width // 2
        goal_y = 150
        self.draw_goal(goal_x, goal_y, goal_width, goal_height)
        
        # ISS風のタイトル画面
        # メインパネル
        panel_width = 600
        panel_height = 320
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        # ISS風の特徴的な青いパネル
        pygame.draw.rect(self.screen, SCOREBOARD_BG, (panel_x, panel_y, panel_width, panel_height))
        
        # パネルの枠（ISS風の二重枠）
        pygame.draw.rect(self.screen, WHITE, (panel_x - 2, panel_y - 2, panel_width + 4, panel_height + 4), 2)
        pygame.draw.rect(self.screen, YELLOW, (panel_x - 6, panel_y - 6, panel_width + 12, panel_height + 12), 2)
        
        # ISS風のロゴ（上部）
        logo_y = panel_y + 30
        
        # ロゴの背景（黒い帯）
        pygame.draw.rect(self.screen, BLACK, (panel_x + 50, logo_y, panel_width - 100, 80))
        pygame.draw.rect(self.screen, WHITE, (panel_x + 50, logo_y, panel_width - 100, 80), 2)
        
        # タイトルテキスト（ISS風の大きな文字）
        title_font = pygame.font.SysFont(None, 60)
        title_text = title_font.render("PENALTY KICK", True, WHITE)
        self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, logo_y + 20))
        
        # ISS風のメニュー選択肢
        menu_y = logo_y + 120
        
        # メニュー項目の背景
        pygame.draw.rect(self.screen, BLACK, (panel_x + 150, menu_y, panel_width - 300, 40))
        pygame.draw.rect(self.screen, WHITE, (panel_x + 150, menu_y, panel_width - 300, 40), 1)
        
        # メニュー項目（点滅効果）
        blink_rate = (pygame.time.get_ticks() % 800) / 800.0
        if blink_rate > 0.4:
            start_text = self.font.render("START GAME", True, YELLOW)
        else:
            start_text = self.font.render("START GAME", True, WHITE)
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, menu_y + 10))
        
        # 操作説明 - キャラクターと重複しないように位置を調整
        instruction_y = menu_y + 120  # 位置を下に移動
        instruction_text = self.font.render("Use arrow keys to aim/save, SPACE to confirm", True, WHITE)
        
        # 説明テキストの背景を追加して読みやすくする
        text_width = instruction_text.get_width() + 20
        text_height = instruction_text.get_height() + 10
        text_bg = pygame.Surface((text_width, text_height))
        text_bg.fill(BLACK)
        text_bg.set_alpha(200)
        self.screen.blit(text_bg, (SCREEN_WIDTH // 2 - text_width // 2, instruction_y - 5))
        
        # テキストを表示
        self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, instruction_y))
        
        # ISS風のキャラクター表示（より大きく、特徴的なポーズ）
        # キッカー（左側）- プレイヤーは青色
        kicker_x = panel_x + 100
        kicker_y = panel_y + panel_height - 80
        self.draw_iss_character(kicker_x, kicker_y, PLAYER_BLUE)
        
        # ゴールキーパー（右側）- AIは赤色
        keeper_x = panel_x + panel_width - 100
        keeper_y = panel_y + panel_height - 80
        self.draw_iss_character(keeper_x, keeper_y, KEEPER_RED, True)
        
        # ボールのアニメーション（ISS風）
        ball_y = panel_y + panel_height - 80 + math.sin(pygame.time.get_ticks() / 300) * 15
        self.draw_iss_ball(SCREEN_WIDTH // 2, int(ball_y))
        
        # ISS風の装飾（フラッシュ効果）
        flash_time = pygame.time.get_ticks() % 5000
        if flash_time < 100:
            flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            flash.fill(WHITE)
            flash.set_alpha(100 - flash_time)
            self.screen.blit(flash, (0, 0))
        
        # ISS風のコピーライト表示
        copyright_text = self.font.render("© 2023 SOCCER GAME", True, WHITE)
        self.screen.blit(copyright_text, (SCREEN_WIDTH // 2 - copyright_text.get_width() // 2, SCREEN_HEIGHT - 30))
    
    def draw_field(self):
        # ISS Deluxe風のフィールドを描画
        
        # 空を描画（上部）
        sky_height = 80
        for y in range(0, sky_height):
            # 空のグラデーション（より鮮やかに）
            gradient_factor = y / sky_height
            sky_color = (
                int(96 + gradient_factor * 32),
                int(176 + gradient_factor * 32),
                int(248)
            )
            pygame.draw.line(self.screen, sky_color, (0, y), (SCREEN_WIDTH, y))
        
        # スタジアムの観客席（背景）
        stand_height = 60
        stand_y = sky_height
        # 観客席の背景
        pygame.draw.rect(self.screen, (64, 64, 80), (0, stand_y, SCREEN_WIDTH, stand_height))
        
        # 観客の表現（ドット状のパターン）
        for y in range(stand_y, stand_y + stand_height, 4):
            for x in range(0, SCREEN_WIDTH, 6):
                # ランダムな色で観客を表現
                if random.random() > 0.7:
                    color = random.choice([(255, 255, 255), (200, 200, 200), (255, 200, 150), (150, 150, 200)])
                    pygame.draw.rect(self.screen, color, (x, y, 2, 2))
        
        # 芝生の背景を塗りつぶし
        pitch_y = sky_height + stand_height
        pygame.draw.rect(self.screen, PITCH_GREEN, (0, pitch_y, SCREEN_WIDTH, SCREEN_HEIGHT - pitch_y))
        
        # ISS風の芝生パターン（横縞模様）
        stripe_count = 12
        stripe_height = (SCREEN_HEIGHT - pitch_y) // stripe_count
        for i in range(stripe_count):
            y = pitch_y + i * stripe_height
            if i % 2 == 0:
                pygame.draw.rect(self.screen, PITCH_DARK, (0, y, SCREEN_WIDTH, stripe_height))
        
        # ペナルティーエリアを描画
        penalty_width = 500
        penalty_height = 240
        penalty_x = SCREEN_WIDTH // 2 - penalty_width // 2
        penalty_y = 180
        
        # ペナルティーエリアの白線
        pygame.draw.rect(self.screen, YELLOW, (penalty_x, penalty_y, penalty_width, penalty_height), 2)
        
        # ゴールエリア（小さい四角形）
        goal_area_width = 200
        goal_area_height = 80
        goal_area_x = SCREEN_WIDTH // 2 - goal_area_width // 2
        goal_area_y = penalty_y
        pygame.draw.rect(self.screen, YELLOW, (goal_area_x, goal_area_y, goal_area_width, goal_area_height), 2)
        
        # ペナルティースポット
        spot_x = SCREEN_WIDTH // 2
        spot_y = penalty_y + 180
        pygame.draw.circle(self.screen, YELLOW, (spot_x, spot_y), 4)
        
        # センターライン
        pygame.draw.line(self.screen, YELLOW, (0, SCREEN_HEIGHT - 180), (SCREEN_WIDTH, SCREEN_HEIGHT - 180), 2)
        
        # センターサークル（部分的に表示）
        pygame.draw.arc(self.screen, YELLOW, 
                       (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT - 250, 140, 140),
                       math.pi, 2 * math.pi, 2)
        
        # センターマーク
        pygame.draw.circle(self.screen, YELLOW, (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 180), 4)
    
    def draw_goal(self, goal_x, goal_y, goal_width, goal_height):
        # ISS Deluxe風のゴールを描画
        
        # ゴールの奥行き表現（3D効果）
        depth = 30
        
        # ゴールの背面（遠近感を出す）
        back_width = goal_width - 20
        back_height = goal_height - 10
        back_x = goal_x + 10
        back_y = goal_y + 5
        
        # ゴールの背面（ネット用の背景）
        pygame.draw.rect(self.screen, NET_WHITE, (back_x, back_y, back_width, back_height))
        
        # ネットの描画（ISS風の斜めパターン）
        net_spacing_h = 15  # 横方向の間隔
        net_spacing_v = 15  # 縦方向の間隔
        
        # 縦線
        for x in range(back_x, back_x + back_width + 1, net_spacing_h):
            pygame.draw.line(self.screen, GOAL_GRAY, (x, back_y), (x, back_y + back_height), 1)
        
        # 横線
        for y in range(back_y, back_y + back_height + 1, net_spacing_v):
            pygame.draw.line(self.screen, GOAL_GRAY, (back_x, y), (back_x + back_width, y), 1)
        
        # 斜め線（ISS風の特徴的なネットパターン）
        for i in range(0, back_width + back_height, net_spacing_h * 2):
            # 左上から右下への斜め線
            start_x = max(back_x, back_x + i - back_height)
            start_y = min(back_y + i, back_y + back_height)
            end_x = min(back_x + i, back_x + back_width)
            end_y = max(back_y, back_y + i - back_width)
            if start_x < back_x + back_width and start_y > back_y:
                pygame.draw.line(self.screen, GOAL_GRAY, (start_x, start_y), (end_x, end_y), 1)
        
        # ゴールの枠（白い太いライン）
        post_thickness = 6
        
        # 左のポスト
        pygame.draw.rect(self.screen, GOAL_POST, (goal_x, goal_y, post_thickness, goal_height))
        # 右のポスト
        pygame.draw.rect(self.screen, GOAL_POST, (goal_x + goal_width - post_thickness, goal_y, post_thickness, goal_height))
        # 上のバー
        pygame.draw.rect(self.screen, GOAL_POST, (goal_x, goal_y, goal_width, post_thickness))
        
        # 奥行きの表現（左ポスト）
        pygame.draw.polygon(self.screen, GOAL_GRAY, [
            (goal_x + post_thickness, goal_y),  # 上端の右
            (back_x, back_y),                   # 背面の左上
            (back_x, back_y + back_height),     # 背面の左下
            (goal_x + post_thickness, goal_y + goal_height)  # 下端の右
        ])
        
        # 奥行きの表現（右ポスト）
        pygame.draw.polygon(self.screen, GOAL_GRAY, [
            (goal_x + goal_width - post_thickness, goal_y),  # 上端の左
            (back_x + back_width, back_y),                   # 背面の右上
            (back_x + back_width, back_y + back_height),     # 背面の右下
            (goal_x + goal_width - post_thickness, goal_y + goal_height)  # 下端の左
        ])
        
        # 奥行きの表現（上バー）
        pygame.draw.polygon(self.screen, GOAL_GRAY, [
            (goal_x + post_thickness, goal_y + post_thickness),  # 左端の下
            (goal_x + goal_width - post_thickness, goal_y + post_thickness),  # 右端の下
            (back_x + back_width, back_y),  # 背面の右上
            (back_x, back_y)                # 背面の左上
        ])
        
        # ゴールのグリッド線（エリア区分用）
        # 縦線
        pygame.draw.line(self.screen, GOAL_GRAY, (goal_x + goal_width // 3, goal_y), 
                        (back_x + back_width // 3, back_y), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (goal_x + 2 * goal_width // 3, goal_y), 
                        (back_x + 2 * back_width // 3, back_y), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (back_x + back_width // 3, back_y), 
                        (back_x + back_width // 3, back_y + back_height), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (back_x + 2 * back_width // 3, back_y), 
                        (back_x + 2 * back_width // 3, back_y + back_height), 1)
        
        # 横線
        pygame.draw.line(self.screen, GOAL_GRAY, (goal_x, goal_y + goal_height // 3), 
                        (back_x, back_y + back_height // 3), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (goal_x, goal_y + 2 * goal_height // 3), 
                        (back_x, back_y + 2 * back_height // 3), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (back_x, back_y + back_height // 3), 
                        (back_x + back_width, back_y + back_height // 3), 1)
        pygame.draw.line(self.screen, GOAL_GRAY, (back_x, back_y + 2 * back_height // 3), 
                        (back_x + back_width, back_y + 2 * back_height // 3), 1)
    
    def draw_iss_character(self, x, y, color, is_keeper=False):
        # ISS Deluxe風のキャラクター
        
        # 影（楕円）
        shadow_width = 20
        shadow_height = 8
        shadow_y = y + 25
        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, shadow_width, shadow_height))
        self.screen.blit(shadow, (x - shadow_width // 2, shadow_y))
        
        # 頭（ISS風の特徴的な形状）
        head_size = 12
        pygame.draw.circle(self.screen, SKIN_COLOR, (x, y - 22), head_size)
        
        # 髪の毛（黒）
        hair_color = BLACK
        pygame.draw.arc(self.screen, hair_color, 
                      (x - head_size, y - 22 - head_size, head_size * 2, head_size * 2),
                      math.pi * 0.7, math.pi * 2.3, 3)
        
        # 顔のディテール
        eye_color = BLACK
        # 目（点）
        pygame.draw.circle(self.screen, eye_color, (x - 4, y - 22), 2)
        pygame.draw.circle(self.screen, eye_color, (x + 4, y - 22), 2)
        
        # 体（ISS風の特徴的なフォルム）
        body_width = 24
        body_height = 30
        
        # 胴体（ユニフォーム）- 渡された色をそのまま使用
        pygame.draw.polygon(self.screen, color, [
            (x - body_width // 2, y - 10),  # 左肩
            (x + body_width // 2, y - 10),  # 右肩
            (x + body_width // 3, y + body_height // 2),  # 右腰
            (x - body_width // 3, y + body_height // 2)   # 左腰
        ])
        
        # ユニフォームの詳細（番号や模様）
        detail_color = WHITE
        pygame.draw.line(self.screen, detail_color, (x - 5, y), (x + 5, y), 2)
        
        # 短パン
        shorts_color = WHITE if color == PLAYER_BLUE else BLACK
        pygame.draw.polygon(self.screen, shorts_color, [
            (x - body_width // 3, y + body_height // 2),  # 左腰
            (x + body_width // 3, y + body_height // 2),  # 右腰
            (x + body_width // 4, y + body_height // 2 + 10),  # 右太もも
            (x - body_width // 4, y + body_height // 2 + 10)   # 左太もも
        ])
        
        # 足（ISS風の特徴的な細い足）
        leg_color = BLACK
        # 左足
        pygame.draw.line(self.screen, leg_color, 
                       (x - body_width // 6, y + body_height // 2 + 10), 
                       (x - body_width // 4, y + body_height), 3)
        # 右足
        pygame.draw.line(self.screen, leg_color, 
                       (x + body_width // 6, y + body_height // 2 + 10), 
                       (x + body_width // 4, y + body_height), 3)
        
        # 靴（ISS風の特徴的な形状）
        shoe_color = BLACK
        # 左靴
        pygame.draw.line(self.screen, shoe_color, 
                       (x - body_width // 4, y + body_height), 
                       (x - body_width // 4 - 5, y + body_height), 4)
        # 右靴
        pygame.draw.line(self.screen, shoe_color, 
                       (x + body_width // 4, y + body_height), 
                       (x + body_width // 4 + 5, y + body_height), 4)
        
        # キーパーの場合は手を広げる
        if is_keeper:
            # 左手
            pygame.draw.line(self.screen, color, 
                           (x - body_width // 2, y - 5), 
                           (x - body_width, y - 15), 3)
            # 右手
            pygame.draw.line(self.screen, color, 
                           (x + body_width // 2, y - 5), 
                           (x + body_width, y - 15), 3)
            # グローブ（ISS風の大きめのグローブ）
            pygame.draw.circle(self.screen, WHITE, (x - body_width, y - 15), 6)
            pygame.draw.circle(self.screen, WHITE, (x + body_width, y - 15), 6)
        else:
            # 通常の腕
            pygame.draw.line(self.screen, color, 
                           (x - body_width // 2, y - 5), 
                           (x - body_width // 2 - 10, y + 5), 3)
            pygame.draw.line(self.screen, color, 
                           (x + body_width // 2, y - 5), 
                           (x + body_width // 2 + 10, y + 5), 3)
    
    def draw_iss_ball(self, x, y):
        # ISS Deluxe風のボール
        ball_radius = 10
        
        # 影（楕円）
        shadow_width = ball_radius * 1.5
        shadow_height = ball_radius * 0.5
        shadow = pygame.Surface((int(shadow_width), int(shadow_height)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), (0, 0, int(shadow_width), int(shadow_height)))
        self.screen.blit(shadow, (x - shadow_width // 2, y + ball_radius))
        
        # ボールの本体（白）
        pygame.draw.circle(self.screen, BALL_WHITE, (x, y), ball_radius)
        
        # ISS風の特徴的な黒い六角形パターン
        pygame.draw.polygon(self.screen, BLACK, [
            (x, y - ball_radius + 3),
            (x + ball_radius - 3, y - ball_radius // 2),
            (x + ball_radius - 3, y + ball_radius // 2),
            (x, y + ball_radius - 3),
            (x - ball_radius + 3, y + ball_radius // 2),
            (x - ball_radius + 3, y - ball_radius // 2)
        ], 2)
        
        # 内側の模様
        pygame.draw.line(self.screen, BLACK, 
                       (x - ball_radius // 2, y), 
                       (x + ball_radius // 2, y), 1)
        pygame.draw.line(self.screen, BLACK, 
                       (x, y - ball_radius // 2), 
                       (x, y + ball_radius // 2), 1)
        
        # ハイライト（光の反射）
        pygame.draw.circle(self.screen, WHITE, (x - ball_radius // 2, y - ball_radius // 2), 3)
    
    def draw_kicking_view(self):
        # フィールドを描画
        self.draw_field()
        
        # ゴールを描画
        goal_width = 400
        goal_height = 200
        goal_x = SCREEN_WIDTH // 2 - goal_width // 2
        goal_y = 150
        
        self.draw_goal(goal_x, goal_y, goal_width, goal_height)
        
        # 現在のターン表示（画面上部右側に移動）
        turn_bg = pygame.Surface((300, 40))
        turn_bg.fill(BLACK)
        self.screen.blit(turn_bg, (SCREEN_WIDTH - 310, 10))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 40), 2)
        
        # チーム表示（青と赤で色分け）
        turn_text = self.font.render("YOUR TURN - KICKER", True, PLAYER_BLUE)
        self.screen.blit(turn_text, (SCREEN_WIDTH - 310 + (300 - turn_text.get_width()) // 2, 20))
        
        # チーム表示（小さく）
        team_font = pygame.font.SysFont(None, 24)
        blue_text = team_font.render("BLUE: YOU", True, PLAYER_BLUE)
        red_text = team_font.render("RED: AI", True, KEEPER_RED)
        self.screen.blit(blue_text, (20, 90))
        self.screen.blit(red_text, (20, 110))
        
        # 選択されたエリアをハイライト（ISS風）
        area_width = goal_width // 3
        area_height = goal_height // 3
        area_x = goal_x + (self.selected_area.value % 3) * area_width
        area_y = goal_y + (self.selected_area.value // 3) * area_height
        
        if self.state == GameState.PLAYER_KICKING:
            # ISS風のターゲットマーカー（点滅する十字線）
            blink_rate = (pygame.time.get_ticks() % 1000) / 1000.0
            if blink_rate > 0.5:
                target_x = area_x + area_width // 2
                target_y = area_y + area_height // 2
                target_size = 20
                
                # 十字線
                pygame.draw.line(self.screen, YELLOW, 
                               (target_x - target_size, target_y), 
                               (target_x + target_size, target_y), 2)
                pygame.draw.line(self.screen, YELLOW, 
                               (target_x, target_y - target_size), 
                               (target_x, target_y + target_size), 2)
                
                # 枠線
                pygame.draw.rect(self.screen, YELLOW, 
                               (area_x, area_y, area_width, area_height), 2)
            
            # ISS風のコマンドウィンドウ
            command_height = 70
            command_y = SCREEN_HEIGHT - command_height - 10
            
            # コマンドウィンドウの背景
            pygame.draw.rect(self.screen, SCOREBOARD_BG, 
                           (10, command_y, SCREEN_WIDTH - 20, command_height))
            pygame.draw.rect(self.screen, WHITE, 
                           (10, command_y, SCREEN_WIDTH - 20, command_height), 2)
            
            # 指示テキスト
            instruction_text = self.font.render("Use arrow keys to aim, SPACE to shoot", True, WHITE)
            self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, command_y + 20))
            
            # パワーメーター（ISS風の特徴的な要素）
            meter_width = 200
            meter_height = 15
            meter_x = SCREEN_WIDTH // 2 - meter_width // 2
            meter_y = command_y + 45
            
            # メーターの背景
            pygame.draw.rect(self.screen, BLACK, (meter_x, meter_y, meter_width, meter_height))
            pygame.draw.rect(self.screen, WHITE, (meter_x, meter_y, meter_width, meter_height), 1)
            
            # メーターの値（時間とともに増減）
            meter_value = (math.sin(pygame.time.get_ticks() / 500) + 1) / 2  # 0～1の間で変動
            pygame.draw.rect(self.screen, RED, 
                           (meter_x + 2, meter_y + 2, 
                            int((meter_width - 4) * meter_value), meter_height - 4))
            
            # キッカーを描画（ISS風）
            self.draw_iss_character(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150, PLAYER_BLUE)
            
            # ボールを描画（ISS風）
            self.draw_iss_ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 110)
        
        elif self.state == GameState.AI_GOALKEEPING:
            # ターン表示を更新（画面右側に配置）
            turn_bg = pygame.Surface((300, 40))
            turn_bg.fill(BLACK)
            self.screen.blit(turn_bg, (SCREEN_WIDTH - 310, 10))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 40), 2)
            
            turn_text = self.font.render("YOUR SHOT - AI KEEPER", True, PLAYER_BLUE)
            self.screen.blit(turn_text, (SCREEN_WIDTH - 310 + (300 - turn_text.get_width()) // 2, 20))
            
            # チーム表示（小さく）
            team_font = pygame.font.SysFont(None, 24)
            blue_text = team_font.render("BLUE: YOU", True, PLAYER_BLUE)
            red_text = team_font.render("RED: AI", True, KEEPER_RED)
            self.screen.blit(blue_text, (20, 90))
            self.screen.blit(red_text, (20, 110))
            
            # AIのセーブ位置をハイライト（ISS風）
            ai_area_x = goal_x + (self.ai_selected_area.value % 3) * area_width
            ai_area_y = goal_y + (self.ai_selected_area.value // 3) * area_height
            
            # AIのセーブ位置マーカー
            keeper_x = ai_area_x + area_width // 2
            keeper_y = ai_area_y + area_height // 2
            
            # 三角飛びメッセージを表示（キック直後）
            if hasattr(self, 'show_sankaku_tobi') and self.show_sankaku_tobi:
                # 特殊メッセージボックス
                special_width = 400
                special_height = 80
                special_x = SCREEN_WIDTH // 2 - special_width // 2
                special_y = SCREEN_HEIGHT // 2 - special_height // 2
                
                # メッセージの背景（黒）と枠（金色）
                pygame.draw.rect(self.screen, BLACK, (special_x, special_y, special_width, special_height))
                pygame.draw.rect(self.screen, GOLD, (special_x, special_y, special_width, special_height), 4)
                
                # 特殊メッセージ（点滅効果）
                blink_rate = (pygame.time.get_ticks() % 300) / 300.0
                if blink_rate > 0.5:
                    special_color = RED
                else:
                    special_color = YELLOW
                
                special_font = pygame.font.SysFont(None, 48)
                special_text = special_font.render("SA N KA KU TO BI !!!", True, special_color)
                self.screen.blit(special_text, (special_x + special_width // 2 - special_text.get_width() // 2, 
                                              special_y + special_height // 2 - special_text.get_height() // 2))
            
            # ゴールキーパーを描画（AIのセーブ位置に、ISS風）- AIは赤色
            self.draw_iss_character(keeper_x, keeper_y, KEEPER_RED, True)
            
            # ボールの軌道を描画（ISS風）- プレイヤーが選択したエリアに向かって飛ぶ
            ball_progress = min(1.0, self.animation_timer / 60)
            selected_area_x = goal_x + (self.selected_area.value % 3) * area_width
            selected_area_y = goal_y + (self.selected_area.value // 3) * area_height
            ball_x = SCREEN_WIDTH // 2 + (selected_area_x + area_width // 2 - SCREEN_WIDTH // 2) * ball_progress
            ball_y = SCREEN_HEIGHT - 110 + (selected_area_y + area_height // 2 - (SCREEN_HEIGHT - 110)) * ball_progress
            
            # ISS風のボールの軌跡（白い点線）
            if ball_progress > 0.1:
                for i in range(1, 8):
                    trail_progress = ball_progress - i * 0.1
                    if trail_progress > 0:
                        trail_x = SCREEN_WIDTH // 2 + (selected_area_x + area_width // 2 - SCREEN_WIDTH // 2) * trail_progress
                        trail_y = SCREEN_HEIGHT - 110 + (selected_area_y + area_height // 2 - (SCREEN_HEIGHT - 110)) * trail_progress
                        pygame.draw.circle(self.screen, WHITE, (int(trail_x), int(trail_y)), 2)
            
            # ボールを描画（ISS風）
            self.draw_iss_ball(int(ball_x), int(ball_y))
    
    def draw_goalkeeping_view(self):
        # フィールドを描画
        self.draw_field()
        
        # ゴールを描画
        goal_width = 400
        goal_height = 200
        goal_x = SCREEN_WIDTH // 2 - goal_width // 2
        goal_y = 150
        
        self.draw_goal(goal_x, goal_y, goal_width, goal_height)
        
        # 現在のターン表示（画面右側に配置）
        turn_bg = pygame.Surface((300, 40))
        turn_bg.fill(BLACK)
        self.screen.blit(turn_bg, (SCREEN_WIDTH - 310, 10))
        pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 40), 2)
        
        turn_text = self.font.render("YOUR TURN - KEEPER", True, PLAYER_BLUE)
        self.screen.blit(turn_text, (SCREEN_WIDTH - 310 + (300 - turn_text.get_width()) // 2, 20))
        
        # チーム表示（小さく）
        team_font = pygame.font.SysFont(None, 24)
        blue_text = team_font.render("BLUE: YOU", True, PLAYER_BLUE)
        red_text = team_font.render("RED: AI", True, KEEPER_RED)
        self.screen.blit(blue_text, (20, 90))
        self.screen.blit(red_text, (20, 110))
        
        # 選択されたエリアをハイライト
        area_width = goal_width // 3
        area_height = goal_height // 3
        area_x = goal_x + (self.selected_area.value % 3) * area_width
        area_y = goal_y + (self.selected_area.value // 3) * area_height
        
        if self.state == GameState.PLAYER_GOALKEEPING:
            # ISS風のセーブポジションマーカー（点滅する十字線）
            blink_rate = (pygame.time.get_ticks() % 1000) / 1000.0
            if blink_rate > 0.5:
                target_x = area_x + area_width // 2
                target_y = area_y + area_height // 2
                target_size = 20
                
                # 十字線
                pygame.draw.line(self.screen, YELLOW, 
                               (target_x - target_size, target_y), 
                               (target_x + target_size, target_y), 2)
                pygame.draw.line(self.screen, YELLOW, 
                               (target_x, target_y - target_size), 
                               (target_x, target_y + target_size), 2)
            
            # ISS風のコマンドウィンドウ
            command_height = 70
            command_y = SCREEN_HEIGHT - command_height - 10
            
            # コマンドウィンドウの背景
            pygame.draw.rect(self.screen, SCOREBOARD_BG, 
                           (10, command_y, SCREEN_WIDTH - 20, command_height))
            pygame.draw.rect(self.screen, WHITE, 
                           (10, command_y, SCREEN_WIDTH - 20, command_height), 2)
            
            # 指示テキスト
            instruction_text = self.font.render("Use arrow keys to choose dive direction, SPACE to confirm", True, WHITE)
            self.screen.blit(instruction_text, (SCREEN_WIDTH // 2 - instruction_text.get_width() // 2, command_y + 20))
            
            # リアクションタイムメーター（ISS風の特徴的な要素）
            meter_width = 200
            meter_height = 15
            meter_x = SCREEN_WIDTH // 2 - meter_width // 2
            meter_y = command_y + 45
            
            # メーターの背景
            pygame.draw.rect(self.screen, BLACK, (meter_x, meter_y, meter_width, meter_height))
            pygame.draw.rect(self.screen, WHITE, (meter_x, meter_y, meter_width, meter_height), 1)
            
            # メーターの値（時間とともに増減）
            meter_value = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2  # 0～1の間で変動（速め）
            pygame.draw.rect(self.screen, YELLOW, 
                           (meter_x + 2, meter_y + 2, 
                            int((meter_width - 4) * meter_value), meter_height - 4))
            
            # ゴールキーパーを描画（ISS風）- プレイヤーは青色
            keeper_x = SCREEN_WIDTH // 2
            keeper_y = goal_y + goal_height + 30
            self.draw_iss_character(keeper_x, keeper_y, PLAYER_BLUE, True)
            
            # AIのキッカーを描画（遠くに小さく、ISS風）- AIは赤色
            kicker_x = SCREEN_WIDTH // 2
            kicker_y = SCREEN_HEIGHT - 80
            
            # 小さいサイズで描画（遠くに見えるように）
            pygame.draw.circle(self.screen, KEEPER_RED, (kicker_x, kicker_y), 8)  # 体
            pygame.draw.circle(self.screen, SKIN_COLOR, (kicker_x, kicker_y - 10), 5)  # 頭
            
            # ボールを描画（ISS風、小さめ）
            ball_x = SCREEN_WIDTH // 2
            ball_y = SCREEN_HEIGHT - 60
            pygame.draw.circle(self.screen, BALL_WHITE, (ball_x, ball_y), 6)
            pygame.draw.circle(self.screen, BLACK, (ball_x, ball_y), 6, 1)
            

        
        elif self.state == GameState.AI_KICKING:
            # ターン表示を更新（画面右側に配置）
            turn_bg = pygame.Surface((300, 40))
            turn_bg.fill(BLACK)
            self.screen.blit(turn_bg, (SCREEN_WIDTH - 310, 10))
            pygame.draw.rect(self.screen, WHITE, (SCREEN_WIDTH - 310, 10, 300, 40), 2)
            
            turn_text = self.font.render("AI SHOT - YOUR SAVE", True, PLAYER_BLUE)
            self.screen.blit(turn_text, (SCREEN_WIDTH - 310 + (300 - turn_text.get_width()) // 2, 20))
            
            # チーム表示（小さく）
            team_font = pygame.font.SysFont(None, 24)
            blue_text = team_font.render("BLUE: YOU", True, PLAYER_BLUE)
            red_text = team_font.render("RED: AI", True, KEEPER_RED)
            self.screen.blit(blue_text, (20, 90))
            self.screen.blit(red_text, (20, 110))
            
            # AIのキック位置をマーク（ISS風）
            ai_area_x = goal_x + (self.ai_selected_area.value % 3) * area_width
            ai_area_y = goal_y + (self.ai_selected_area.value // 3) * area_height
            
            # プレイヤーのセーブ位置をマーク（ISS風）
            save_x = area_x + area_width // 2
            save_y = area_y + area_height // 2
            
            # 三角飛びメッセージを表示（キック直後）
            if hasattr(self, 'show_sankaku_tobi') and self.show_sankaku_tobi:
                # 特殊メッセージボックス
                special_width = 400
                special_height = 80
                special_x = SCREEN_WIDTH // 2 - special_width // 2
                special_y = SCREEN_HEIGHT // 2 - special_height // 2
                
                # メッセージの背景（黒）と枠（金色）
                pygame.draw.rect(self.screen, BLACK, (special_x, special_y, special_width, special_height))
                pygame.draw.rect(self.screen, GOLD, (special_x, special_y, special_width, special_height), 4)
                
                # 特殊メッセージ（点滅効果）
                blink_rate = (pygame.time.get_ticks() % 300) / 300.0
                if blink_rate > 0.5:
                    special_color = RED
                else:
                    special_color = YELLOW
                
                special_font = pygame.font.SysFont(None, 48)
                special_text = special_font.render("SA N KA KU TO BI !!!", True, special_color)
                self.screen.blit(special_text, (special_x + special_width // 2 - special_text.get_width() // 2, 
                                              special_y + special_height // 2 - special_text.get_height() // 2))
            
            # セーブマーカー（点滅する円）
            blink_rate = (pygame.time.get_ticks() % 500) / 500.0
            if blink_rate > 0.3:
                pygame.draw.circle(self.screen, YELLOW, (save_x, save_y), 20, 2)
            
            # プレイヤーのゴールキーパーを描画（セーブ位置に、ISS風）- プレイヤーは青色
            self.draw_iss_character(save_x, save_y, PLAYER_BLUE, True)
            
            # ISS風のダイビングエフェクト（動きの表現）
            if self.animation_timer > 20:
                # ダイビングの軌跡（点線）
                start_x = SCREEN_WIDTH // 2
                start_y = goal_y + goal_height + 30
                for i in range(1, 6):
                    progress = i / 5.0
                    trail_x = start_x + (save_x - start_x) * progress
                    trail_y = start_y + (save_y - start_y) * progress
                    pygame.draw.circle(self.screen, WHITE, (int(trail_x), int(trail_y)), 2)
            
            # ボールの軌道を描画（ISS風）
            ball_progress = min(1.0, self.animation_timer / 60)
            ball_x = SCREEN_WIDTH // 2 + (ai_area_x + area_width // 2 - SCREEN_WIDTH // 2) * ball_progress
            ball_y = SCREEN_HEIGHT - 60 + (ai_area_y + area_height // 2 - (SCREEN_HEIGHT - 60)) * ball_progress
            
            # ISS風のボールの軌跡（白い点線）
            if ball_progress > 0.1:
                for i in range(1, 8):
                    trail_progress = ball_progress - i * 0.1
                    if trail_progress > 0:
                        trail_x = SCREEN_WIDTH // 2 + (ai_area_x + area_width // 2 - SCREEN_WIDTH // 2) * trail_progress
                        trail_y = SCREEN_HEIGHT - 60 + (ai_area_y + area_height // 2 - (SCREEN_HEIGHT - 60)) * trail_progress
                        pygame.draw.circle(self.screen, WHITE, (int(trail_x), int(trail_y)), 2)
            
            # ボールを描画（ISS風）
            self.draw_iss_ball(int(ball_x), int(ball_y))
    
    def draw_pixel_trophy(self, x, y):
        pixel_size = 8
        gold_color = (255, 215, 0)
        
        # トロフィーの上部（カップ部分）
        for i in range(3):
            pygame.draw.rect(self.screen, gold_color, (x - pixel_size * 2, y - pixel_size * (3 - i), pixel_size * 4, pixel_size))
        
        # トロフィーの柄の部分
        pygame.draw.rect(self.screen, gold_color, (x - pixel_size // 2, y, pixel_size, pixel_size * 2))
        
        # トロフィーの台座
        pygame.draw.rect(self.screen, gold_color, (x - pixel_size * 2, y + pixel_size * 2, pixel_size * 4, pixel_size))
    
    def draw_snes_trophy(self, x, y):
        # スーパーファミコン風のトロフィー（より詳細で立体的）
        gold_color = GOLD
        highlight_color = WHITE
        shadow_color = (180, 150, 50)
        
        # トロフィーのカップ部分
        pygame.draw.ellipse(self.screen, gold_color, (x - 30, y - 50, 60, 20))  # 上部
        pygame.draw.rect(self.screen, gold_color, (x - 25, y - 40, 50, 40))  # 本体
        
        # ハイライト（光の反射）
        pygame.draw.line(self.screen, highlight_color, (x - 20, y - 45), (x - 10, y - 45), 2)
        pygame.draw.line(self.screen, highlight_color, (x - 20, y - 30), (x - 10, y - 30), 2)
        
        # 取っ手
        pygame.draw.ellipse(self.screen, gold_color, (x - 40, y - 35, 15, 30))  # 左
        pygame.draw.ellipse(self.screen, gold_color, (x + 25, y - 35, 15, 30))  # 右
        
        # 台座
        pygame.draw.rect(self.screen, gold_color, (x - 15, y, 30, 10))  # 柄
        pygame.draw.rect(self.screen, gold_color, (x - 25, y + 10, 50, 10))  # 台
        
        # 台座のハイライト
        pygame.draw.line(self.screen, highlight_color, (x - 25, y + 10), (x + 25, y + 10), 2)
        
        # キラキラエフェクト（スーパーファミコン風の装飾）
        star_time = pygame.time.get_ticks() / 200
        for i in range(3):
            star_x = x + math.cos(star_time + i * 2) * 15
            star_y = y - 30 + math.sin(star_time + i) * 10
            star_size = 2 + math.sin(star_time * 2 + i) * 1
            pygame.draw.circle(self.screen, WHITE, (int(star_x), int(star_y)), int(star_size))
    
    def draw_result(self):
        # フィールドを描画（背景として）
        self.draw_field()
        
        # ゴールを描画（装飾として）
        goal_width = 400
        goal_height = 200
        goal_x = SCREEN_WIDTH // 2 - goal_width // 2
        goal_y = 150
        self.draw_goal(goal_x, goal_y, goal_width, goal_height)
        
        # ISS風の結果画面
        # メインパネル
        panel_width = 600
        panel_height = 400
        panel_x = SCREEN_WIDTH // 2 - panel_width // 2
        panel_y = SCREEN_HEIGHT // 2 - panel_height // 2
        
        # ISS風の特徴的な結果パネル（黒背景）
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)
        
        # 上部の結果バナー
        banner_height = 80
        if self.player_score > self.ai_score:
            banner_color = BLUE  # 勝利時は青
        elif self.player_score < self.ai_score:
            banner_color = RED   # 敗北時は赤
        else:
            banner_color = YELLOW  # 引き分け時は黄色
        
        pygame.draw.rect(self.screen, banner_color, (panel_x, panel_y, panel_width, banner_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, banner_height), 2)
        
        # 結果テキスト（ISS風の大きな文字）
        result_font = pygame.font.SysFont(None, 60)
        if self.player_score > self.ai_score:
            result_text = result_font.render("YOU WIN!", True, WHITE)
            # ISS風の勝利演出（トロフィーと星）
            self.draw_snes_trophy(SCREEN_WIDTH // 2, panel_y + banner_height + 60)
            
            # 星のエフェクト
            star_time = pygame.time.get_ticks() / 200
            for i in range(8):
                angle = star_time / 10 + i * math.pi / 4
                distance = 80 + math.sin(star_time / 5 + i) * 20
                star_x = SCREEN_WIDTH // 2 + math.cos(angle) * distance
                star_y = panel_y + banner_height + 60 + math.sin(angle) * distance
                pygame.draw.polygon(self.screen, YELLOW, [
                    (star_x, star_y - 10),
                    (star_x + 3, star_y - 3),
                    (star_x + 10, star_y - 3),
                    (star_x + 5, star_y + 3),
                    (star_x + 7, star_y + 10),
                    (star_x, star_y + 5),
                    (star_x - 7, star_y + 10),
                    (star_x - 5, star_y + 3),
                    (star_x - 10, star_y - 3),
                    (star_x - 3, star_y - 3)
                ])
        elif self.player_score < self.ai_score:
            result_text = result_font.render("AI WINS!", True, WHITE)
        else:
            result_text = result_font.render("DRAW", True, WHITE)
        
        self.screen.blit(result_text, (SCREEN_WIDTH // 2 - result_text.get_width() // 2, panel_y + banner_height // 2 - result_text.get_height() // 2))
        
        # ISS風のスコアボード
        score_y = panel_y + banner_height + 150
        score_height = 60
        
        # スコアボードの背景
        pygame.draw.rect(self.screen, SCOREBOARD_BG, (panel_x + 100, score_y, panel_width - 200, score_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x + 100, score_y, panel_width - 200, score_height), 2)
        
        # チーム名と得点
        team_font = pygame.font.SysFont(None, 40)
        player_text = team_font.render("PLAYER", True, WHITE)
        vs_text = team_font.render("VS", True, YELLOW)
        ai_text = team_font.render("AI", True, WHITE)  # CPUからAIに変更
        
        score_font = pygame.font.SysFont(None, 50)
        player_score_text = score_font.render(str(self.player_score), True, YELLOW)
        ai_score_text = score_font.render(str(self.ai_score), True, YELLOW)
        
        # テキスト配置 - 等間隔に配置
        score_box_width = panel_width - 200
        total_width = player_text.get_width() + player_score_text.get_width() + vs_text.get_width() + ai_score_text.get_width() + ai_text.get_width()
        spacing = (score_box_width - total_width) / 4  # 5つの要素間に4つの間隔
        
        x_pos = panel_x + 100 + spacing/2
        self.screen.blit(player_text, (x_pos, score_y + 10))
        x_pos += player_text.get_width() + spacing
        self.screen.blit(player_score_text, (x_pos, score_y + 10))
        x_pos += player_score_text.get_width() + spacing
        self.screen.blit(vs_text, (x_pos, score_y + 10))
        x_pos += vs_text.get_width() + spacing
        self.screen.blit(ai_score_text, (x_pos, score_y + 10))
        x_pos += ai_score_text.get_width() + spacing
        self.screen.blit(ai_text, (x_pos, score_y + 10))
        
        # ラウンド結果表示は削除
        
        # ISS風の再スタートオプション
        restart_y = panel_y + panel_height - 60
        
        # 点滅効果
        blink_rate = (pygame.time.get_ticks() % 800) / 800.0
        if blink_rate > 0.4:
            restart_text = self.font.render("PRESS SPACE TO CONTINUE", True, YELLOW)
        else:
            restart_text = self.font.render("PRESS SPACE TO CONTINUE", True, WHITE)
        
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, restart_y))

if __name__ == "__main__":
    game = PKGame()
    game.run()