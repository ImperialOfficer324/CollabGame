import pygame

pygame.init()

window = pygame.display.set_mode((800,800))

class button():
    def __init__(self,x,y,w,h,img):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.img = img
        self.down = False
        self.idle_state = 0
        self.hover_state = 0
        self.click_state = 0
    def update(self,surface):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        
        #update animation states
        self.idle_state+=1
        if self.idle_state//25>=len(self.img[0]):self.idle_state = 0
        self.hover_state+=1
        if self.hover_state//25>=len(self.img[1]):self.hover_state = 0
        self.click_state+=1
        if self.click_state//25>=len(self.img[2]):self.click_state = 0
        
        if (self.x + self.w > mouse[0] and mouse[0] > self.x ) and (self.y + self.h > mouse[1] and mouse[1] > self.y):
            if click[0]==1:
                self.down = True
                image = pygame.transform.scale(self.img[2][self.click_state//25],(self.w,self.h))
                surface.blit(image,(self.x,self.y))
            else:
                img = pygame.transform.scale(self.img[1][self.hover_state//25],(self.w,self.h))
                surface.blit(img,(self.x,self.y))
                if self.down:
                    self.down = False
                    return True
        else:
            self.down = False
            image = pygame.transform.scale(self.img[0][self.idle_state//25],(self.w,self.h))
            surface.blit(image,(self.x,self.y))
            
        return False

button_play_temp = pygame.transform.scale(pygame.image.load("assets/gui/button_play.png"),(600,100))
img_button_play = []
for i in range(0,3):
    temp_surface = pygame.Surface((200,100))
    temp_surface.set_colorkey((0,0,0))
    temp_surface.blit(button_play_temp,(0,0),( i*200,0, 200,100))
    img_button_play.append([temp_surface])

def load_page(state):
    widgets = []
    if state == 0:
        button_play = button(300,200,200,100,img_button_play)
        widgets.append(button_play)
    
    return widgets

def update_current_menu(state):
    if state == 0: #Opening Screen
        for widget in widgets:
            widget.update(window)
    
    return state

menu_state = 0
widgets = load_page(menu_state)

run = True
while run:
    window.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()

    menu_state = update_current_menu(menu_state)

    pygame.display.update()