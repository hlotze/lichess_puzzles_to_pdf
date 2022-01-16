##########################################
# that script 'generate_theme_puzzles.py
# processes data take from
# https://database.lichess.org/
#
# i.e. chess puzzles with
#   -- initial FEN, and
#   -- its next moves (in uci-notation)
# 
# now produce html files for some
# these puzzles
##########################################

import os  # for mkdir

import chess
import chess.pgn
import chess.svg
import numpy as np
import pandas as pd

from sqlalchemy import create_engine

#######################################
# generate a file "my_secrets.py" 
# with
#   user = '<your user name>'
#   password = '<your password>'
#   server = '<your server name>'
#   database = '<your  database name>'
#######################################
from my_secrets import user, password, server, database

db_connection_str = 'mysql+pymysql://'+user+':'+password+'@'+server+'/'+database
db_connection = create_engine(db_connection_str)



def gen_page_header(d, page):
    out = ""
    out = out + """\
            <table align='center' style='width:100%'>\n \
                <tr style='vertical-align:top'>\n \
                    <td style='width:50%' align='left'><strong><em>\
                        Lichess Puzzles - """+d['Theme']+" ["+str(d['num'])+"/"+str(d['all'])+"""]</em></strong></td>\n \
                    <td style='width:'50%' align='right'><strong><a href='"""+\
                        d["GameURL"]+"' target='_blank'>"+d["GameURL"]+\
                        """</a></strong></td>\n \
                </tr>\n"""
    if ('1st page' == page):
        out = out + """
                <tr>\n \
                    <td style='width:50%' align='left'><em>"""+d['Comment']+"""</em></td>\n \
                    <td style='width:'50%' align='right'> <!-- --> </td>\n \
                </tr>\n""" 
    out = out + """
            </table>\n \
            <br>\n"""
    return(out)


######################################################
#
# MAIN
#
######################################################
# get all Themes (and Theme_set) that are of interest
tg_df = pd.read_sql('SELECT * FROM Themes_by_groups', con=db_connection)

# list of theme_groups Theme_short
# to generate puzzle PDFs from
themes_l = list(np.unique(tg_df['Theme_short'].to_list()))

# walk over all ~60 theme_shorts and prepare some (10) Puzzles of each themell
# for development start with a short list of themes --> just 1 
# [-1:] --> the last of the list
# e.g. only 'zugzwang'
for ts in themes_l[:-5]:
    # get 10 puzzles of the theme_set
    select_str = "SELECT * FROM Theme_{TS} LIMIT 10".format(TS = ts)
    #print(select_str)
    reqp_df = pd.read_sql(select_str, con=db_connection)
    #print(reqp_df)
    
    ##############################################
    # for each puzzle of the theme_set
    #
    # 1.) prepare the puzzle's data
    # 2.) generate the html layout and out_file
    ##############################################

    for ix in range(len(reqp_df)):
        ##############################
        # prepare that puzzle's data
        # for further processing
        act_p_dict            = reqp_df.iloc[ix][['ix', 'FEN', 'Moves', 'GameURL']].to_dict()
        act_p_dict['Theme']   = tg_df[tg_df['Theme_set'] == ts]['Theme'].to_list()[0]
        act_p_dict['Comment'] = tg_df[tg_df['Theme_set'] == ts]\
            ['Comment'].to_list()[0].replace('>', '&gt;').replace('<', '&lt;').replace('\n','<br>')
        act_p_dict['num']     = ix + 1
        act_p_dict['all']     = len(reqp_df)
        act_p_dict['out_dir'] = "html/Theme_"+ts+"/"
        act_p_dict['out_file_name'] = ts+"_"+("0000"+str(ix + 1))[-5:]+".html"
        #print(act_p_dict)
        #print('---------------------')

        #######################################
        # prepare the puzzle's moves
        # with
        # act_p_move_dict = {
        #     'full_move_num' : 0,    # as given vom FEN for the actual game's situation
        #     'active_player' : '',   # w_hite or b_lack
        #     'san'           : '',   # chess standard algebraic notation
        #     'move_str'      : '',   # for a white's move: 38. Bg3 
        #                             # for a black's move: 38. ... Bg3
        #     'svg'           : '',   # the board's actual diagram
        #     'is_start'      : False # False for a normal move, True for the start diagramm
        # }
        act_p_move_dict = {}

        # and put it into at moves list for that puzzle
        act_p_moves_list = []

        # a list of strings of the moves of that puzzle
        # in uci notation
        moves_str_lst = act_p_dict["Moves"].split(" ")
        # board of that puzzle
        board = chess.Board(fen=act_p_dict["FEN"])
        # define the board's viewpoint aka orientation
        orientation = board.turn


        move = board.push_uci(moves_str_lst[0])
        # get next active_player
        if (chess.WHITE == board.turn):
            act_p_move_dict['active_player'] = 'w'
        else:
            act_p_move_dict['active_player'] = 'b'
        
        # un-do the move to
        board.pop() 
        
        # get full_move_number
        act_p_move_dict['full_move_num'] = board.fullmove_number
        # get SAN of move
        act_p_move_dict['san'] = board.san(move)
        # prepare move_str
        if (chess.WHITE == board.turn):
            act_p_move_dict['move_str'] = str(act_p_move_dict['full_move_num'])+". <strong>"+act_p_move_dict['san']+"</strong>"
        else:  
            act_p_move_dict['move_str'] = str(act_p_move_dict['full_move_num'])+". ... <strong>"+act_p_move_dict['san']+"</strong>"
        
        move = board.push_uci(moves_str_lst[0])

        # this is the start diagram
        act_p_move_dict['is_start'] = True

        # svg of 1st diagram
        # i.e. first page of the puzzle
        #      the puzzle's question
        if board.is_check():
            for sq in chess.SQUARES:
                if (chess.KING == board.piece_type_at(sq) and (board.turn == board.color_at(sq))):
                    act_p_move_dict['svg'] = chess.svg.board(board, 
                                                             size=600, 
                                                             check=sq, 
                                                             lastmove=move, 
                                                             flipped=orientation)
                    break
        else:
            act_p_move_dict['svg'] = chess.svg.board(board, 
                                                     size=600, 
                                                     lastmove=move, 
                                                     flipped=orientation)
        
        act_p_moves_list.append(act_p_move_dict.copy())

        page = 0
        ######################################
        # all remaining moves of that puzzle
        for mv_str in moves_str_lst[1:]: ## all remaining moves
            act_p_move_dict = {}
            act_p_move_dict['is_start'] = False

            move = board.push_uci(mv_str)
            board.pop() # to sync FEN with move stack

            # get active_player        
            if (chess.WHITE == board.turn):
                act_p_move_dict['active_player'] = 'w'
            else:
                act_p_move_dict['active_player'] = 'b'

            # get full_move_number
            act_p_move_dict['full_move_num'] = board.fullmove_number
            # get SAN of move
            act_p_move_dict['san'] = board.san(move)
            # prepare move_str
            if (chess.WHITE == board.turn):
                act_p_move_dict['move_str'] = str(act_p_move_dict['full_move_num'])+". <strong>"+act_p_move_dict['san']+"</strong>"
            else:  
                act_p_move_dict['move_str'] = str(act_p_move_dict['full_move_num'])+". ... <strong>"+act_p_move_dict['san']+"</strong>"            
            
            # Board Anzeige
            move = board.push_uci(mv_str)
            arrow = chess.svg.Arrow(tail=move.from_square,
                                    head=move.to_square)

            if board.is_check():
                for sq in chess.SQUARES:
                    if (chess.KING == board.piece_type_at(sq) and (board.turn == board.color_at(sq))):
                        act_p_move_dict['svg'] = chess.svg.board(board, 
                                                                size=280, 
                                                                check=sq,
                                                                arrows=[arrow],
                                                                lastmove=move, 
                                                                flipped=orientation)
                        break
            else:
                act_p_move_dict['svg'] = chess.svg.board(board, 
                                                        size=280, 
                                                        arrows=[arrow],
                                                        lastmove=move,
                                                        flipped=orientation)
            
            act_p_moves_list.append(act_p_move_dict.copy())
        
        #print("data prep done for", ts, ix+1, "len of moves", len(act_p_moves_list))
        
        ###############################################
        # all puzzle's data and moves now prepared
        # now start html layout and page generation
        #
        # -- puzzle's data  --> at act_p_dict
        # -- puzzle's moves --> at act_p_moves_list
        #                          -- act_p_move_dict
        #                          -- act_p_move_dict
        #                          -- ...
        ###############################################
        L = [] # output buffer for html file

        # 1st page with puzzle's question
        L.append("""<!doctype html>\n
        <html>\n
            <head>\n
                <title>Lichess Puzzles - """+ act_p_dict['Theme'] +" ["+ str(act_p_dict['num']) +"/"+str(act_p_dict['all'])+"""]</title>\n
                <style>\n
                    @media print {\n
                        .pagebreak { page-break-after: always; } /* page-break-before works, as well */ \n
                    }\n
                    @page { size: A4 }\n
                </style>\n
            </head>\n
            <body>\n
            """)

        L.append(gen_page_header(act_p_dict, "1st page"))
        mv = act_p_moves_list[0]
        if ('w' == mv['active_player']):
            site_to_move = "White"
        else:
            site_to_move = "Black"
        L.append("What is the best move for "+site_to_move+"<br>\nafter<br>\n") # question page
        L.append(mv['move_str']+"\n")
        L.append("<br>\n")
        L.append("<center>\n")
        L.append(mv['svg'])
        L.append("</center>\n")
        L.append("<div class='pagebreak'> </div>\n")

        page = 1
        L.append(gen_page_header(act_p_dict, "solution"))
        L.append("Solution page "+str(page)+"\n") # solution pages
        L.append("<table align='center' border=0 cellspacing=2 cellpadding=5>\n")
        
        ##################################
        # all remaining moves
        # puzzle's solution

        # 3 lines of w + b diagramms / page
        line = 0

        ply = 0
        for mv in act_p_moves_list[1:]:
            if (0 == ply % 2):
                L.append("  <tr style='vertical-align:top'>\n")

            if (0 == ply and 'b' == mv['active_player']):
                L.append("    <td style='width:50%'></td>")
                ply += 1

            #L.append("    <td style='width:50%'>"+mv['move_str']+"\n<br>\n"+"<br>\n</td>\n")
            L.append("    <td style='width:50%'>"+mv['move_str']+"<br>"+mv['svg']+"<br></td>")
            ply += 1           

            if (0 == ply % 2):
                L.append("  </tr>\n")
                line += 1

            if (0 == line % 3 and 0 == ply % 2 and  ply <= len(act_p_moves_list)-1):
                L.append("</table>\n")
                L.append("<div class='pagebreak'> </div>\n")
                page += 1
                L.append(gen_page_header(act_p_dict, "solution"))
                L.append("Solution page "+str(page)+"\n") # solution pages
                L.append("<table align='center' border=0 cellspacing=2 cellpadding=5>\n")
        
        if (0 == page % 2 ):
                L.append("</table>\n")
                L.append("<div class='pagebreak'> </div>\n")
                L.append(gen_page_header(act_p_dict, "empty"))
                L.append("empty page\n") # solution pages                
                L.append("<table align='center' border=0 cellspacing=2 cellpadding=5>\n")
                for i in range(15):
                    L.append("<tr><td>&nbsp;<br><!-- empty page --></td></tr>\n")

        ##################################
        # all moves done for this puzzle
        # store to html file
        L.append(\
            """
                </table>
            </body>
            </html>
            """ )
        
        # mkdir for "Theme_<theme>", e.g. Theme_zugzwang
        if not os.path.exists(act_p_dict['out_dir']):
            os.makedirs(act_p_dict['out_dir'])
        
        print(act_p_dict['out_dir']+act_p_dict['out_file_name'])
        f = open(act_p_dict['out_dir']+act_p_dict['out_file_name'], "w")
        f.writelines(L)
        f.close()
        L = []

        # mkdir for pdf files
        if not os.path.exists(act_p_dict['out_dir'].replace('html', 'pdf')):
            os.makedirs(act_p_dict['out_dir'].replace('html', 'pdf'))

