import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import VGG19_Weights
import os
import urllib.request

class AdaIN(nn.Module):
    def __init__(self):
        super(AdaIN, self).__init__()

    def forward(self, content, style):
        # Adaptive Instance Normalization
        content_mean, content_std = self.calc_mean_std(content)
        style_mean, style_std = self.calc_mean_std(style)
        normalized = (content - content_mean) / content_std
        return normalized * style_std + style_mean

    def calc_mean_std(self, feat, eps=1e-5):
        size = feat.size()
        assert (len(size) == 4)
        N, C = size[:2]
        feat_var = feat.view(N, C, -1).var(dim=2) + eps
        feat_std = feat_var.sqrt().view(N, C, 1, 1)
        feat_mean = feat.view(N, C, -1).mean(dim=2).view(N, C, 1, 1)
        return feat_mean, feat_std

class Encoder(nn.Module):
    def __init__(self):
        super(Encoder, self).__init__()
        vgg = models.vgg19(weights=VGG19_Weights.DEFAULT).features
        self.layers = nn.Sequential(*list(vgg.children())[:21])  # Up to relu4_1

    def forward(self, x):
        return self.layers(x)

class Decoder(nn.Module):
    def __init__(self):
        super(Decoder, self).__init__()
        self.layers = nn.Sequential(
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(512, 256, (3, 3)),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(256, 256, (3, 3)),
            nn.ReLU(),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(256, 256, (3, 3)),
            nn.ReLU(),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(256, 256, (3, 3)),
            nn.ReLU(),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(256, 128, (3, 3)),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(128, 128, (3, 3)),
            nn.ReLU(),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(128, 64, (3, 3)),
            nn.ReLU(),
            nn.Upsample(scale_factor=2, mode='nearest'),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(64, 64, (3, 3)),
            nn.ReLU(),
            nn.ReflectionPad2d((1, 1, 1, 1)),
            nn.Conv2d(64, 3, (3, 3)),
        )
        self.load_weights()

    def load_weights(self):
        model_dir = '/models'
        if not os.path.exists(model_dir):
            os.makedirs(model_dir)
        weight_path = os.path.join(model_dir, 'decoder.pth')
        if not os.path.exists(weight_path):
            url = 'https://github.com/naoto0804/pytorch-AdaIN/raw/master/models/decoder.pth'
            urllib.request.urlretrieve(url, weight_path)
        self.load_state_dict(torch.load(weight_path, map_location='cpu'))
        return self.layers(x)


# Example: Add a second style transfer model (CartoonStyleTransferModel)
class CartoonStyleTransferModel(nn.Module):
    def __init__(self):
        super(CartoonStyleTransferModel, self).__init__()
        # For demo, reuse Encoder/Decoder, but in practice, use a different architecture/weights
        self.encoder = Encoder()
        self.adain = AdaIN()
        self.decoder = Decoder()

    def forward(self, content, style):
        # For demo, same as StyleTransferModel
        content_feat = self.encoder(content)
        style_feat = self.encoder(style)
        adain_feat = self.adain(content_feat, style_feat)
        output = self.decoder(adain_feat)
        return output

class StyleTransferModel(nn.Module):
    def __init__(self, model_type: str = 'adain'):
        super(StyleTransferModel, self).__init__()
        if model_type == 'cartoon':
            self.model = CartoonStyleTransferModel()
        else:
            self.model = self._adain_model()

    def _adain_model(self):
        class AdaINModel(nn.Module):
            def __init__(self):
                super().__init__()
                self.encoder = Encoder()
                self.adain = AdaIN()
                self.decoder = Decoder()
            def forward(self, content, style):
                content_feat = self.encoder(content)
                style_feat = self.encoder(style)
                adain_feat = self.adain(content_feat, style_feat)
                output = self.decoder(adain_feat)
                return output
        return AdaINModel()

    def forward(self, content, style):
        return self.model(content, style)