# poker_probability_app.py

import streamlit as st
from itertools import combinations
from random import sample
from treys import Deck, Evaluator, Card


def validate_cards(cards):
    """
    Validate the user-input cards to ensure they are valid and correctly formatted.

    Parameters:
        cards (list): List of cards as strings (e.g., ['As', 'Kd']).

    Returns:
        bool: True if all cards are valid, False otherwise.
    """
    valid_ranks = "23456789TJQKA"
    valid_suits = "shdc"
    for card in cards:
        if len(card) != 2 or card[0] not in valid_ranks or card[1] not in valid_suits:
            return False
    return True


def calculate_win_probability(hole_cards, board_cards, num_players, num_simulations=10000):
    """
    Calculate the probability of winning with the given hole cards and board.

    Parameters:
        hole_cards (list): Two hole cards as strings (e.g., ['As', 'Kd']).
        board_cards (list): Community cards as strings (e.g., ['Qs', 'Jh', '9d']).
        num_players (int): Number of players in the game.
        num_simulations (int): Number of simulations to run.

    Returns:
        float: Probability of winning as a percentage.
    """
    evaluator = Evaluator()
    deck = Deck()

    # Convert hole and board cards to integers
    try:
        hole_card_ints = [Card.new(card) for card in hole_cards]
        board_card_ints = [Card.new(card) for card in board_cards]
    except KeyError as e:
        raise ValueError(f"Invalid card: {e}")

    # Remove the used cards from the deck
    for card in hole_card_ints + board_card_ints:
        if card in deck.cards:
            deck.cards.remove(card)
        else:
            raise ValueError(f"Card {Card.int_to_str(card)} is not available in the deck.")

    wins = 0

    # Run simulations
    for _ in range(num_simulations):
        # Deal opponents' hands and remaining board cards
        opponents_hands = [sample(deck.cards, 2) for _ in range(num_players - 1)]
        remaining_board = sample(
            [c for c in deck.cards if c not in sum(opponents_hands, [])], 5 - len(board_cards)
        )
        final_board = board_card_ints + remaining_board

        # Evaluate hero's hand
        hero_score = evaluator.evaluate(final_board, hole_card_ints)

        # Evaluate opponents' hands
        opponent_scores = [
            evaluator.evaluate(final_board, opp_hand) for opp_hand in opponents_hands
        ]

        # Check if hero wins
        if hero_score <= min(opponent_scores):
            wins += 1

    return (wins / num_simulations) * 100  # Return win probability as a percentage


# Streamlit App
st.title("Poker Hand Probability Calculator")
st.markdown(
    """
    **Instructions**:
    1. Enter your two hole cards (e.g., `As`, `Kd` for Ace of Spades and King of Diamonds).
    2. Enter the community cards (flop, turn, and river) as they appear.
    3. Select the number of players.
    4. Click "Calculate Probability" to see your chances of winning.
    """
)

# User Input
hole_cards = st.text_input(
    "Enter your hole cards (e.g., 'As Kd'):", placeholder="As Kd"
).split()
board_cards = st.text_input(
    "Enter the board cards (e.g., 'Qs Jh 9d'):", placeholder="Qs Jh 9d"
).split()
num_players = st.slider("Number of players (including you):", 2, 10, 2)

# Validate Input
if len(hole_cards) != 2:
    st.error("Please enter exactly 2 hole cards.")
elif len(board_cards) > 5:
    st.error("You can enter a maximum of 5 board cards.")
elif not validate_cards(hole_cards + board_cards):
    st.error("One or more cards are invalid. Please use the format 'As' (Ace of Spades).")
else:
    # Calculate Probability
    if st.button("Calculate Probability"):
        try:
            win_probability = calculate_win_probability(
                hole_cards, board_cards, num_players
            )
            st.success(f"Your probability of winning is {win_probability:.2f}%")
        except ValueError as e:
            st.error(f"Error calculating probability: {e}")
        except Exception as e:
            st.error(f"Unexpected error: {e}")
