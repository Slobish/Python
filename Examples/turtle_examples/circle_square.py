import turtle

def draw_square( ang, length, p):
    # Draw a square
    
    p.lt( ang )
    for i in range(4):
        p.forward( length )
        p.lt( 90 )
    p.rt( ang )

def circle_square(radius, p):
    # Draw a circle by drawing many squares

    for ang in range(0, 360, 10):
        draw_square( ang, radius, p)

if __name__ == "__main__":    
    window = turtle.Screen()

    t_main = turtle.Turtle()
    t_main.speed(0)

    circle_square(100, t_main )

    window.exitonclick()
