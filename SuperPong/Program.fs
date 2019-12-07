namespace SuperPong

open Microsoft.Xna.Framework
open Microsoft.Xna.Framework.Graphics;
open Microsoft.Xna.Framework.Input;

type PongGame() as this = 
    inherit Game()

    let graphics = new GraphicsDeviceManager(this)
    let mutable spriteBatch = Unchecked.defaultof<SpriteBatch>

    override __.LoadContent() = 
        spriteBatch <- new SpriteBatch(this.GraphicsDevice)

    override __.Update(gameTime) =
        ()

    override __.Draw(gameTime) =
        this.GraphicsDevice.Clear Color.LemonChiffon

module Entry =
    [<EntryPoint>]
    let main _ =
        use game = new PongGame()
        game.Run()
        0