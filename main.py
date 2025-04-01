import os
import analyzer
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Political Audio Analyzer")
    parser.add_argument('input_file', help='Path to the input audio file')
    parser.add_argument('-t', '--test', action='store_true', required=False, help='Run in test mode')

    args = parser.parse_args()
    
    # Get and print transcript
    transcript = analyzer.get_transcript(os.path.dirname(args.input_file), os.path.basename(args.input_file))
    print("\nTranscript:")
    print(transcript)
