import pygame
import random
import math

class Cell:
	def __init__(self,pos,w,h,rcol):
		self.pos = pos
		self.width = w
		self.height = h
		self.gcost = 0
		self.hcost = 0
		self.fcost = 0
		self.do_color = False
		self.base_color = rcol
		self.select_color = (255,0,0) # red
		self.impassable = False

	def __eq__(self,other):
		return self.pos.x == other.pos.x and self.pos.y == other.pos.y

	def __ne__(self,other):
		return self.pos.x != other.pos.x or self.pos.y != other.pos.y

	def mark_passable(self):
		self.impassable = False

	def mark_impassable(self):
		self.impassable = True

	def unselect(self):
		self.do_color = False

	def select(self):
		self.do_color = True

	def did_hit(self,mousevec):
		xhit = mousevec.x >= self.pos.x and mousevec.x <= (self.pos.x + self.width)
		yhit = mousevec.y >= self.pos.y and mousevec.y <= (self.pos.y + self.height)
		return xhit and yhit

	def update_costs(self, start_pos, end_pos):
		self.gcost = math.hypot(start_pos.pos.x - self.pos.x, start_pos.pos.y - self.pos.y)
		self.hcost = math.hypot(end_pos.pos.x - self.pos.x, end_pos.pos.y - self.pos.y)
		self.fcost = self.gcost + self.hcost

	def draw(self,surface):
		ccol = self.select_color if self.do_color else self.base_color
		if self.impassable:
			pygame.draw.rect(surface, self.base_color, (self.pos.x,self.pos.y,self.width,self.height))
		else:
			pygame.draw.rect(surface, ccol, (self.pos.x,self.pos.y,self.width,self.height), 1)

def get_neighbors(cells,cell):
	neighbors = []
	xidx = 0
	yidx = 0
	found = False

	for row in cells:
		if found:
			break
		xidx = 0
		for xcell in row:
			if xcell == cell:
				found = True
				#print("found cell at",xidx,yidx)
				break
			xidx += 1
		if found:
			break
		yidx += 1

	for i in range(yidx - 1, yidx + 2):
		for j in range(xidx - 1, xidx + 2):
			#print("i,j",i,j)
			if i < 0 or j < 0 or i >= len(cells) or j >= len(cells[0]):
				continue
			if i == yidx and j == xidx:
				continue
			ncell = cells[i][j]
			if ncell.impassable:
				continue
			neighbors.append(ncell)
			#print("added neighbor",i,j)

	return neighbors

def astar(cells, start, end):
	xopen = []
	xclosed = []

	for row in cells:
		for cell in row:
			# start and end must be vectors
			cell.update_costs(start, end)
			
	if start.impassable:
		print("Cannot mark impassable cell as a start cell in search")
		return []

	xopen.append(start)
	while len(xopen) > 0:
		#print("xopen", xopen)
		#print("xclosed", xclosed)
		fcost_sel = 999999
		cell_sel = None
		cell_idx = -1
		for i,itm in enumerate(xopen):
			if itm.fcost < fcost_sel:
				fcost_sel = itm.fcost
				cell_sel = itm
				cell_idx = i

		if cell_sel is None:
			break
		del xopen[cell_idx]
		xclosed.append(cell_sel)

		#print("Visited",cell_sel.pos.x,cell_sel.pos.y)

		# Hit the target
		if cell_sel == end:
			#print("Hit the target cell")
			return xclosed

		next_path = 999999
		for neighbor in get_neighbors(cells, cell_sel):
			if cell.impassable or neighbor in xclosed:
				continue
			xopen.append(neighbor)

	return xclosed

def cell_select(cells, path_cells, mark_impassable=False):
	for row in cells:
		for cell in row:
			cell.unselect()
			mx,my = pygame.mouse.get_pos()
			if cell.did_hit(pygame.math.Vector2(mx,my)):
				if mark_impassable:
					cell.mark_impassable()
				else:
					if not cell.impassable:
						cell.select()
						path_cells.append(cell)

def main(winx=800,winy=600):
	done = False
	cells = []
	cell_width = 50
	cell_height = 50
	rancol = (random.randrange(0,255), random.randrange(0,255), random.randrange(0,255))

	for y in range(0,winy,cell_height):
		row = []
		for x in range(0,winx,cell_width):
			cell = Cell(pygame.math.Vector2(x,y),cell_width,cell_height,rancol)
			row.append(cell)
		cells.append(row)

	pygame.display.init()
	screen = pygame.display.set_mode((winx,winy))
	clock = pygame.time.Clock()
	selected = False
	rendered = False
	path_cells = []
	while not done:
		clock.tick(30)  # limits FPS to 60
		# Input
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				done = True
				break
			elif e.type == pygame.MOUSEBUTTONDOWN:
				if e.button == 1 and not rendered:
					if selected:
						cell_select(cells, path_cells)
						touched_cells = astar(cells, path_cells[0], path_cells[-1])
						for cell in touched_cells:
							cell.select()
						rendered = True
					else:
						# select a cell
						cell_select(cells, path_cells)
						selected = True
				elif e.button == 3 and not selected:
					cell_select(cells, path_cells, True)
				elif e.button == 3 and selected:
					print("Must mark impassable cells before selecting/rendering")
					print("Press 'Space' to reset")
			elif e.type == pygame.KEYDOWN:
				if e.key == pygame.K_SPACE:
					# reset
					selected = False
					rendered = False
					path_cells = []
					for row in cells:
						for cell in row:
							cell.unselect()
							cell.mark_passable()
				if e.key == pygame.K_ESCAPE:
					done = True
					break

		screen.fill((0,0,0))

		for row in cells:
			for cell in row:
				cell.draw(screen)

		pygame.display.flip()

	pygame.display.quit()

if __name__ == "__main__":
	main()
