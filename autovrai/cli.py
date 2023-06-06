import argparse

from autovrai import model_loader, process_image_directory


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AutoVR.ai - an AI-powered toolkit for converting 2D media into immersive VR using local hardware')

    parser.add_argument('images', type=[], help='Path to image directory')

    parser.add_argument('--stereo', type=str, default='', help='Stereo option')
    parser.add_argument('--padded', type=str, default='', help='Padded option')
    parser.add_argument('--anaglyph', type=str, default='', help='Anaglyph option')
    parser.add_argument('--depthmap', type=str, default='', help='Depthmap option')
    parser.add_argument('--depthraw', type=str, default='', help='Depthraw option')

    parser.add_argument('--divergence', type=float, default=2.5, help='Divergence value')

    args = parser.parse_args()

    config = {
        'model': 'zoedepth_nk',
        'device': 'gpu'
    }

    model = model_loader(config['model'], config['device'])
    process_image_directory(model, config)
