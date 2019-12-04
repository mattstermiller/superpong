namespace SuperPong

open Microsoft.Xna.Framework
open Microsoft.Xna.Framework.Graphics;
open Microsoft.Xna.Framework.Input;
open MonoGame.Extended

module Values =
    let gameSize = Vector2(1.5f, 1.0f)
    let wallSize = 0.045f

    module Paddle =
        let size = Size2(0.024f, 0.145f)
        let xOffset = 0.6f
        let maxYOffset = gameSize.Y/2.f - size.Height/2.f - wallSize
        let speed = 1.1f
        let colors = [Color(32, 32, 240); Color(192, 32, 32)]

[<AutoOpen>]
module Extensions =
    type Vector2 with
        member this.ToPoint2 () = Point2(this.X, this.Y)

    type Size2 with
        member this.Scale (scale: Vector2) = Size2(this.Width * scale.X, this.Height * scale.Y)

type Viewport = {
    SizeFactor: Vector2
    PosFactor: Vector2
    PosTranslate: Vector2
}
with
    member this.GetScreenPos (pos: Vector2) = ((pos + this.PosTranslate) * this.PosFactor).Round 0
    member this.GetScreenSize (size: Size2) = size.Scale this.SizeFactor

    member this.GetScreenRect (center: Vector2, size: Size2) =
        let topLeft = center + Vector2(-size.Width/2.f, size.Height/2.f)
        RectangleF(this.GetScreenPos(topLeft).ToPoint2(), this.GetScreenSize(size))

    static member Default = {
        SizeFactor = Vector2()
        PosFactor = Vector2()
        PosTranslate = Vector2()
    }

    static member Create(screenArea: Rectangle, cameraSize: Vector2, cameraCenter: Vector2, invertY) =
        let screenSize = screenArea.Size.ToVector2()
        let screenPos = screenArea.Location.ToVector2()
        let yFactor = Vector2(1.f, if invertY then -1.f else 1.f)
        let sizeFactor = screenSize / cameraSize
        {   SizeFactor = sizeFactor
            PosFactor = sizeFactor * yFactor
            PosTranslate =
                (cameraSize / 2.f - cameraCenter) +
                (screenPos * cameraSize) / screenSize * yFactor +
                (if invertY then Vector2(0.f, -cameraSize.Y) else Vector2.Zero)
        }

type Paddle = {
    Pos: float32
    Vel: float32
}
with
    static member Default = { Pos = 0.f; Vel = 0.f }

type GameState = {
    Viewport: Viewport
    Paddles: Paddle list
}

type Event =
    | SetPaddleDir of player: int * dir: int
    | Update of GameTime

module Logic =
    let updatePaddle index f state =
        { state with Paddles = state.Paddles |> List.mapi (fun i p -> if i = index then f p else p) }

    let updatePaddlePos time paddle =
        let pos = paddle.Pos + paddle.Vel * time |> min Values.Paddle.maxYOffset |> max -Values.Paddle.maxYOffset
        { paddle with Pos = pos }

    let handle (state: GameState) = function
        | SetPaddleDir (player, dir) ->
            state |> updatePaddle player (fun p -> { p with Vel = float32 dir * Values.Paddle.speed })
        | Update t ->
            let time = t.GetElapsedSeconds()
            state
            |> updatePaddle 0 (updatePaddlePos time)
            |> updatePaddle 1 (updatePaddlePos time)

open Logic

type PongGame() as this = 
    inherit Game()

    let graphics = new GraphicsDeviceManager(this)
    let mutable spriteBatch = Unchecked.defaultof<SpriteBatch>

    let mutable state = {
        Viewport = Viewport.Default
        Paddles = List.init 2 (fun _ -> Paddle.Default)
    }

    override __.LoadContent() = 
        spriteBatch <- new SpriteBatch(this.GraphicsDevice)
        let viewport = Viewport.Create(this.GraphicsDevice.Viewport.Bounds, Values.gameSize, Vector2.Zero, true)
        state <- { state with Viewport = viewport }

    override __.Update(gameTime) =
        let keyState = Keyboard.GetState()
        let keys = keyState.GetPressedKeys()
        if keys |> Seq.contains Keys.Escape then
            this.Exit()
        let getDir upKey downKey =
            if keys |> Seq.contains upKey then 1
            else if keys |> Seq.contains downKey then -1
            else 0
        let events = seq {
            yield SetPaddleDir (0, getDir Keys.W Keys.S)
            yield SetPaddleDir (1, getDir Keys.Up Keys.Down)
            yield Update gameTime
        }
        state <- events |> Seq.fold handle state

    override __.Draw(gameTime) =
        this.GraphicsDevice.Clear Color.Black
        let view = state.Viewport
        spriteBatch.Begin()
        let drawPaddle index =
            let x = Values.Paddle.xOffset * (if index = 0 then -1.f else 1.f)
            let rect = view.GetScreenRect(Vector2(x, state.Paddles.[index].Pos), Values.Paddle.size)
            let color = Values.Paddle.colors.[index]
            spriteBatch.DrawRectangle(rect, color, rect.Width)
        drawPaddle 0
        drawPaddle 1

        let wallSize = Size2(Values.gameSize.X, Values.wallSize) |> view.GetScreenSize
        let topPos = Values.gameSize / Vector2(-2.f, 2.f) |> view.GetScreenPos
        let bottomPos = -Values.gameSize/2.f + Vector2(0.f, Values.wallSize) |> view.GetScreenPos
        spriteBatch.DrawRectangle(topPos, wallSize, Color.White, wallSize.Height/2.f)
        spriteBatch.DrawRectangle(bottomPos, wallSize, Color.White, wallSize.Height/2.f)

        spriteBatch.End()

module Entry =
    [<EntryPoint>]
    let main _ =
        use game = new PongGame()
        game.Run()
        0