from copy import deepcopy
from os import sep
import numpy as np

black_player = 1
white_player = 2

class Board:
    def __init__(self,size,previous_board,board):
        self.size = size
        self.previous_board = previous_board
        self.board = board

    def find_neighbors(self, move):
        neighbors = set()
        row = move[0]
        column = move[1]
        if row > 0: neighbors.add((row-1, column))
        if row < self.size - 1: neighbors.add((row+1, column))
        if column > 0: neighbors.add((row, column-1))
        if column < self.size - 1: neighbors.add((row, column+1))
        return neighbors

    def find_like_friends(self, move,board_state):
        #print("Friend Row "+str(row))
        #print("Friend Column "+str(column))
        #print(board_state[row][column])

        neighbors = self.find_neighbors(move)
        neighbor_friends = set()
        for neighbor in neighbors:
            if board_state[neighbor[0]][neighbor[1]] != 0  and board_state[neighbor[0]][neighbor[1]] == board_state[move[0]][move[1]]:
                neighbor_friends.add(neighbor)
        return neighbor_friends

    def find_board_friends(self, move,board_state):
        stack = [(move[0], move[1])]  
        friends = [] 
        while len(stack) > 0:
            stone_position = stack.pop()
            friends.append(stone_position)
            neighbors = self.find_like_friends(stone_position,board_state)
            for neighbor in neighbors:
                if neighbor not in stack and neighbor not in friends:
                    stack.append(neighbor)
        return friends

    def find_liberty(self, move,board_state):
        board_friends = self.find_board_friends(move,board_state)
        #print("Row "+str(row))
        #print("Column "+str(column))
        #print("Player "+str(board_state[row][column]))
        #print("board friends")
        #print(board_friends)
        player_friends = set()
        for friend in board_friends:
            neighbors = self.find_neighbors(friend)
            for neighbor in neighbors:
                if board_state[neighbor[0]][neighbor[1]] == 0:
                    player_friends.add(neighbor)
        #print("Liberty Count = "+str(len(player_friends)))
        #print(player_friends)
        return len(player_friends)

    def find_dead_stones(self, player,board_state):
        dead_stones = set()
        for row in range(0,self.size):
            for column in range(0,self.size):
                if board_state[row][column] == player:
                    if self.find_liberty((row, column), board_state) == 0:
                        dead_stones.add((row,column))
        return dead_stones

    def remove_dead_stones(self, player,board_state):
        dead_stones = self.find_dead_stones(player,board_state)
        if not dead_stones: return []
        self.remove_stones(dead_stones,board_state)
        return dead_stones

    def remove_stones(self, positions,board_state):
        for stone in positions:
            board_state[stone[0]][stone[1]] = 0
            
    
    def find_opponent_liberty(self,move,player,board_state):
        neighbors = self.find_neighbors(move)
        opp_liberty_count = 0
        for neighbor in neighbors:
            if board_state[neighbor[0]][neighbor[1]] == 3 - player:
                opp_liberty_count+=self.find_liberty(neighbor,board_state)
        return opp_liberty_count

    def obtain_possible_moves(self, board_state,player):
        possible_moves = set()
        for row in range(0, self.size):
            for column in range(0,self.size):
                if self.is_move_valid(board_state,player,row,column):                                    
                    possible_moves.add((row,column))
        return possible_moves

    def is_move_valid(self,board_state,player,row,column):
        new_board = deepcopy(board_state)
        if row < 0 or row >= self.size or column < 0 or column >= self.size:
            return False
        if new_board[row][column] != 0:
            return False
        new_board[row][column] = player
        if self.find_liberty((row,column),new_board) == 0:
            self.remove_dead_stones(3 - player,new_board)
            if self.find_liberty((row,column), new_board) > 0:
                return self.does_not_violates_GO_rule(new_board)
            return False
        return True
    
    def does_not_violates_GO_rule(self,board_state):
        #if (self.previous_board == self.board).all():
        if (self.previous_board == self.board):
            return True
        #if (self.previous_board == board_state).all():
        if (self.previous_board == board_state):
            return False       
        return True

    def find_near_opponents(self, player,board_state,move):
        board_friends = self.find_board_friends(move,board_state)
        player_friends = set()
        for friend in board_friends:
            neighbors = self.find_neighbors(friend)
            for neighbor in neighbors:
                if board_state[neighbor[0]][neighbor[1]] == 3-player:
                    player_friends.add(neighbor)
        return len(board_friends) - len(player_friends)

    def is_edge_move(self,move):
        neighbors = self.find_neighbors(move)
        return len(neighbors) < 4
    
    def is_corner_move(self,move):
        neighbors = self.find_neighbors(move)
        return len(neighbors) < 3

    def make_eyes(self, board_state,player):
        q1=0
        q3 =0 
        qd = 0
        row = 0
        column = 0
        while row < self.size:
            while column < self.size:
                if board_state[row][column] == player:
                    q1+=1
                if row+1 < self.size:
                    if board_state[row+1][column] == player:
                        q1+=1
                    if column+1 < self.size:
                        if board_state[row][column] == player and board_state[row+1][column] == player and board_state[row+1][column+1] == player:
                            q3+=1
                        if board_state[row][column+1] == player and board_state[row][column] == player and board_state[row+1][column] == player:
                            q3+=1
                        if board_state[row][column] == player and board_state[row][column+1] == player and board_state[row+1][column+1] == player:
                            q3+=1
                        if board_state[row][column+1] == player and board_state[row+1][column+1] == player and board_state[row+1][column] == player:
                            q3+1
                        if board_state[row][column] == player and board_state[row+1][column+1] == player:
                            qd+=1
                        if board_state[row+1][column] == player and board_state[row][column+1] == player:
                            qd+=1
                        if board_state[row+1][column+1] == player:
                            q1+=1
                if column +1 < self.size and board_state[row][column+1] == player:
                    q1+=1
                column+=1
            row+=1
        total_eyes = (q1 - q3 + (2*qd))//4
        return total_eyes
                    
                    
                        

class AlphaBetaAgent:
    def __init__(self):
        self.type = "AlphaBeta"
        
    def calculate_player_max_score(self,player,board_state,go_board,move):
        black_stones = 0
        white_stones = 0
        black_positions = set()
        white_positions = set()
        for row in range(0,go_board.size):
            for column in range(0,go_board.size):
                stone = board_state[row][column]
                if stone == black_player:
                    black_stones+=1
                    black_positions.add((row,column))
                if stone == white_player:
                    white_stones+=1
                    white_positions.add((row,column))
        diff = abs(black_stones - white_stones)
        liberty_count = self.calculate_player_liberty(board_state,go_board,player,black_positions,white_positions)
        new_board_state = deepcopy(board_state)
        captured_stones = go_board.remove_dead_stones(3 - player,new_board_state)
        is_edge_move = go_board.is_edge_move(move)
        near_opponents_count = go_board.find_near_opponents(player,board_state,move)
        opp_liberty = go_board.find_opponent_liberty(move,player,board_state)
        corner_move = go_board.is_corner_move(move)
        if is_edge_move:
            diff+=-2
        if corner_move:
            diff+=-2
        connected_group = go_board.find_board_friends(move,board_state)
        total_eyes = go_board.make_eyes(board_state,player)
        diff+= len(connected_group)+total_eyes
        return diff+liberty_count+len(captured_stones)+near_opponents_count - opp_liberty

    def calculate_player_liberty(self,board_state,go_board,player,black_positions,white_positions):
        black_liberty_count = 0
        white_liberty_count = 0
        for black in black_positions:
            board_friends = go_board.find_board_friends(black,board_state)
            for friend in board_friends:
                neighbors = go_board.find_neighbors(friend)
                for neighbor in neighbors:
                    if board_state[neighbor[0]][neighbor[1]] == 0:
                        black_liberty_count+=1 
        for white in white_positions:
            board_friends = go_board.find_board_friends(white,board_state)
            for friend in board_friends:
                neighbors = go_board.find_neighbors(friend)
                for neighbor in neighbors:
                    if board_state[neighbor[0]][neighbor[1]] == 0:
                        white_liberty_count+=1 

        if player == black_player:
            return black_liberty_count - white_liberty_count
        else:
            return white_liberty_count - black_liberty_count
    

    def alpha_beta_pruning(self,depth,alpha,beta,is_max_player,move,go_board,board_state,player):
        if depth == 0:
            return (self.calculate_player_max_score(player,board_state,go_board,move),move)
        if is_max_player:
            moves = go_board.obtain_possible_moves(board_state,player)
            max_score= (-5000,move)
            for possible_move in moves:
                new_state = deepcopy(board_state)
                new_state[possible_move[0]][possible_move[1]] = player
                go_board.remove_dead_stones(3 - player,new_state)
                score = self.alpha_beta_pruning(depth-1,alpha,beta,False,possible_move,go_board,new_state,3-player)
                if score[0] > max_score[0]:
                    max_score = (score[0],possible_move)
                if score[0] > alpha:
                    alpha = score[0]
                if beta <= alpha:
                    break
            return max_score
        else:
            moves = go_board.obtain_possible_moves(board_state,player)
            min_score= (5000,move)
            for possible_move in moves:
                new_state = deepcopy(board_state)
                new_state[possible_move[0]][possible_move[1]] = player
                go_board.remove_dead_stones(3 - player,new_state)
                score = self.alpha_beta_pruning(depth-1,alpha,beta,True,possible_move,go_board,new_state,3-player)
                if score[0] < min_score[0]:
                    min_score = (score[0],possible_move)
                if score[0] < beta:
                    beta = score[0]
                if beta <= alpha:
                    break
            return min_score

    def get_input(self,go_game,player):
        go_board = Board(go_game.size,go_game.previous_board,go_game.board)
        board_state = deepcopy(go_game.board)
        play_move_details = self.alpha_beta_pruning(4,-5000,5000,True,None,go_board,board_state,player)
        play_move = play_move_details[1]
        if play_move is None:
            return "PASS"
        else:
            return play_move



def main():
    file = open("input.txt",'r')
    player = int(file.readline().rstrip())
    prev_board_state = np.zeros([5,5],dtype=int)
    current_board_state = np.zeros([5,5],dtype=int)
    for i in range(0,5):
        line_values = list(file.readline().rstrip())
        for j in range(0,len(line_values)):
            prev_board_state[i][j] = int(line_values[j])
    for i in range(0,5):
        line_values = list(file.readline().rstrip())
        for j in range(0,len(line_values)):
            current_board_state[i][j] = int(line_values[j])
    go_board = Board(5,prev_board_state,current_board_state)
    player_move = AlphaBetaAgent()
    player_move_value = player_move.alpha_beta_pruning(4,-5000,5000,True,None,go_board,current_board_state,player)
    play_move = player_move_value[1]
    write_file = open("output.txt","w")
    if play_move == None:
        write_file.write("PASS")    
    else:
        write_output = [str(play_move[0]),str(play_move[1])]
        write_file.write(",".join(write_output))
    write_file.close()

if __name__ == '__main__':
    main()   
