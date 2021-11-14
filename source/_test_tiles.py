import pygame

window = pygame.display.set_mode((1000,700))

def display_tiles():
    for row in range(0,20):
        for column in range(0,14):
            pygame.draw.rect(window,(row*10,column*10,100),(row*50,column*50,50,50))
    pygame.draw.circle(window,(255,255,255),(mouse_point[0],mouse_point[1]),5)
    return 1

mouse_point = (0,0)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(pygame.mouse.get_pos())
            mouse_point = pygame.mouse.get_pos()
    window.fill((0,0,0))
    display_tiles()
    pygame.display.update()