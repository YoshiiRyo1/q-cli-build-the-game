## 準備

https://aws.amazon.com/jp/blogs/news/build-games-with-amazon-q-cli-and-score-a-t-shirt/

[Amazon Q CLI](https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/command-line-installing.html) と [PyGame](https://www.pygame.org/wiki/GettingStarted) をインストール


VS Codeの拡張機能をインストール
https://marketplace.visualstudio.com/items?itemName=AmazonWebServices.amazon-q-vscode


```
q cli はローカルPCのファイルを読み書きできる？
```

![alt text](image.png)

 ## やってみた

```
python, PyGame を使ってゲームを作る。あなたはゲーム開発者だ。サッカーのPKをするゲームだ。詳細は要件定義をしてほしい。あなたが私に質問するのだ。
```

![alt text](image-1.png)


```
1つずつ答えていく。

1.全年齢向け

2.シングルプレイヤー、プレイヤーとAIは交互にキッカーとゴールキーパーを担当

3.難易度は必要ない

4.疑似3D。キッカーを後ろから見ている視点

5.キーボード操作

6.5回のPKで終わり、サドンデスは無し

7.簡易なアニメーションを希望

8.サウンドは不要

9.提示された追加機能は不要

10.まず基本機能を実装

回答を基に仕様書を作成して。仕様はinstructions.md に保存。
```

![alt text](image-2.png)

```
ゲーム開発を開始して。基本的なゲームフレームワークから開始。
```

![alt text](image-3.png)


```
グラフィックの改善から始めよう。サッカーのゴール、ピッチの芝、ペナルティーエリアの白線を描いて。
```

```
日本語が正しく表示されない。ゲーム内は英語で表記して。
```

```
キャラクターをドット風の3頭身で描いて。それに合わせてボールやゴール枠、ピッチも変更。
```

```
描写を改善したい。SNES（スーパーファミコン）のようなゲーム画面にしたい。
このようなイメージ → https://www.gavas.jp/upload/save_image/2978_4.jpg
```

```
プレイヤーが蹴るセルを選択し、ボールを蹴るが、選択したセルにボールが飛んでいかない。
AI キーパーが選択したセルにボールが飛ぶアニメーションになってしまっている。ゴールは決まっているので描写が異常だと判断している。
調査・修正して。
```

```
プレーヤーがキッカーのターンなのか、キーパーのターンなのか分かりにくい。
プレーヤーは青色のユニフォーム、AI は赤色のユニフォームで統一して。
```

```
視覚的な一貫性、がまだ修正されていない。もう一度修正して。
プレイヤーが操作するキャラクターは常に青色
AIが操作するキャラクターは常に赤色
キッカーとキーパーの役割が入れ替わっても色は変わらない
```

```
'ss/title_overlap.png' を参照して。文字列 'Use arrow keys to ...' がキャラクターと重複している。重複しないように修正して。
```

![alt text](image-4.png)

```
プレイ中画面上部に表示される 'YOUR TURN ...' が左上のスコア領域を重複している。重複しないよう修正して。
```

```
ゲーム中に表示される 'SHOT!', 'READY!', 'SAVE!' は不要。描写しないで。
```

```
以下のエラーを修正して
File "/Users/ryo.yoshii/github/q-cli-build-the-game/pk_game.py", line 824
    def draw_goalkeeping_view(self):
IndentationError: unexpected indent
```

```
5回目のPKが終わった段階で以下のエラー。修正して。

Traceback (most recent call last):
  File "/Users/ryo.yoshii/github/q-cli-build-the-game/pk_game.py", line 1169, in <module>
    game.run()
    ~~~~~~~~^^
  File "/Users/ryo.yoshii/github/q-cli-build-the-game/pk_game.py", line 92, in run
    self.draw()
    ~~~~~~~~~^^
  File "/Users/ryo.yoshii/github/q-cli-build-the-game/pk_game.py", line 216, in draw
    self.draw_result()
    ~~~~~~~~~~~~~~~~^^
  File "/Users/ryo.yoshii/github/q-cli-build-the-game/pk_game.py", line 1070, in draw_result
    self.draw_iss_trophy(SCREEN_WIDTH // 2, panel_y + banner_height + 60)
    ^^^^^^^^^^^^^^^^^^^^
AttributeError: 'PKGame' object has no attribute 'draw_iss_trophy'. Did you mean: 'draw_snes_trophy'?
```

```
PK が終わり 'AI WINS', 'YOU WIN!', "DRAW" が表示されるところで、最後のキックの結果、例えば 'GOAL CONCENDED!' が消えずに残ってしまう。消すように修正して。
```

```
プレイ中の画面でスコア表示が 'PLAYER 0 VS 0 CPU' になっている。以下のように修正して。
PLAYER ◯ ◯ ✗ ◯ ◯
AI ◯ ◯ ✗ ◯ ✗
```

```
日本語が正しく表示されません。◯✗ではなくアルファベットで効果的に表示して。
```

```
スコアの表示について。想定している2段になっていない。
'PLAYER OOOXXOOO AI' のように PLAYER にすべて表示されてしまう。修正して。
```

```
スコア部分のラウンド表示は不要。削除して。
```

```
リザルト画面に表示されているスコアに余分なスペースが含まれている。
player_score_text, vs_test, ai_score_text を等間隔に修正して。
```

（ソースは見ないはずだったけど我慢できず）

```
ゴールキーパーは10%の確率で必ずセーブするようなロジックを入れて。
10% に当選した場合はポップアップで 'SA N KA KU TO BI !!!' という文字列を表示すること。
```

```
「SA N KA KU TO BI !!!」というテキストはキッカーがキックした後すぐに表示して。今はゴールキーパーのセーブ後に表示されている。
また、三角飛び当選時のボールの軌跡とキーパーのいるセルがずれている。キッカーが選んだセルにキーパーを強制移動させて。
```

```
「SA N KA KU TO BI !!!」メッセージの表示されるが、ゴールが決まってしまっている。三角飛び時は必ずセーフするように修正して。
```

```
「SA N KA KU TO BI !!!」メッセージの表示タイミングがずれている。抽選で当選した次のキックでメッセージが表示されている。キーパーのセーブは前の回で行われているように思う。
```

```

```

```

```

```

```
