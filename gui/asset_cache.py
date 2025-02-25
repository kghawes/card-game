from kivy.graphics import Rectangle

class AssetCache:
    """Manages cached assets like textures to prevent redundant loading."""
    _textures = {}

    @staticmethod
    def get_texture(image_path):
        if image_path not in AssetCache._textures:
            AssetCache._textures[image_path] = Rectangle(source=image_path).texture
        return AssetCache._textures[image_path]