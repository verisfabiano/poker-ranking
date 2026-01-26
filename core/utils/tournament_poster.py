"""
Gerador avançado de posters para divulgação de torneios
Design moderno, chamativo e profissional
"""
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from io import BytesIO
from pathlib import Path

try:
    import qrcode
    HAS_QRCODE = True
except ImportError:
    HAS_QRCODE = False


class TournamentPosterGenerator:
    """Gera imagens de divulgação para torneios de poker com design profissional"""
    
    DIMENSIONS = {
        'story': (1080, 1920),
        'feed': (1080, 1440),
        'horizontal': (1920, 1080),
    }
    
    THEMES = {
        'gold': {
            'bg': (20, 20, 30),
            'primary': (218, 165, 32),
            'secondary': (255, 255, 255),
            'accent': (220, 20, 60),
            'text_light': (200, 200, 210),
            'card_bg': (50, 50, 70),
            'gradient_1': (40, 30, 50),
            'gradient_2': (20, 20, 30),
        },
        'dark': {
            'bg': (15, 15, 25),
            'primary': (100, 200, 255),
            'secondary': (255, 255, 255),
            'accent': (255, 100, 100),
            'text_light': (180, 180, 200),
            'card_bg': (40, 40, 60),
            'gradient_1': (30, 50, 80),
            'gradient_2': (15, 15, 25),
        },
        'neon': {
            'bg': (10, 10, 20),
            'primary': (0, 255, 200),
            'secondary': (255, 255, 255),
            'accent': (255, 50, 100),
            'text_light': (150, 255, 200),
            'card_bg': (30, 50, 60),
            'gradient_1': (20, 40, 50),
            'gradient_2': (10, 10, 20),
        }
    }
    
    def __init__(self, tournament, template='feed', theme='gold'):
        self.tournament = tournament
        self.template = template
        self.theme_name = theme
        self.theme = self.THEMES.get(theme, self.THEMES['gold'])
        
        dim = self.DIMENSIONS.get(template, self.DIMENSIONS['feed'])
        self.WIDTH, self.HEIGHT = dim
        
        self.image = None
        self.draw = None
        
    def _get_font(self, size, bold=False):
        """Obtém fonte TTF"""
        font_paths = [
            Path('/System/Library/Fonts'),
            Path('/usr/share/fonts/truetype'),
            Path('C:/Windows/Fonts'),
        ]
        
        font_names = ['arial', 'Arial', 'DejaVuSans', 'Helvetica']
        suffix = 'Bold' if bold else ''
        
        for font_dir in font_paths:
            if not font_dir.exists():
                continue
            for font_name in font_names:
                font_file = font_dir / f'{font_name}{suffix}.ttf'
                if font_file.exists():
                    try:
                        return ImageFont.truetype(str(font_file), size)
                    except:
                        pass
        
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()
    
    def _create_background(self):
        """Cria background com gradiente"""
        self.image = Image.new('RGB', (self.WIDTH, self.HEIGHT), self.theme['bg'])
        self.draw = ImageDraw.Draw(self.image, 'RGBA')
        
        # Adicionar efeito de gradiente sutil
        for y in range(self.HEIGHT):
            ratio = y / self.HEIGHT
            r = int(self.theme['gradient_1'][0] * (1 - ratio) + self.theme['gradient_2'][0] * ratio)
            g = int(self.theme['gradient_1'][1] * (1 - ratio) + self.theme['gradient_2'][1] * ratio)
            b = int(self.theme['gradient_1'][2] * (1 - ratio) + self.theme['gradient_2'][2] * ratio)
            self.draw.line([(0, y), (self.WIDTH, y)], fill=(r, g, b))
    
    def _draw_rounded_rect(self, xy, fill, outline, width=2, radius=20):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = xy
        
        # Desenhar cantos arredondados
        self.draw.ellipse([x1, y1, x1+radius*2, y1+radius*2], fill=fill, outline=outline, width=width)
        self.draw.ellipse([x2-radius*2, y1, x2, y1+radius*2], fill=fill, outline=outline, width=width)
        self.draw.ellipse([x1, y2-radius*2, x1+radius*2, y2], fill=fill, outline=outline, width=width)
        self.draw.ellipse([x2-radius*2, y2-radius*2, x2, y2], fill=fill, outline=outline, width=width)
        
        # Desenhar retângulos
        self.draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
        self.draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
        
        # Desenhar bordas
        self.draw.line([(x1+radius, y1), (x2-radius, y1)], fill=outline, width=width)
        self.draw.line([(x2, y1+radius), (x2, y2-radius)], fill=outline, width=width)
        self.draw.line([(x2-radius, y2), (x1+radius, y2)], fill=outline, width=width)
        self.draw.line([(x1, y2-radius), (x1, y1+radius)], fill=outline, width=width)
    
    def _add_title_story(self):
        """Template STORY com design chamatvo"""
        y = 50
        
        # Dia semana em caixa preta
        if self.tournament.data:
            dias = ['SEGUNDA', 'TERÇA', 'QUARTA', 'QUINTA', 'SEXTA', 'SÁBADO', 'DOMINGO']
            dia_semana = dias[self.tournament.data.weekday()]
            hora_str = self.tournament.data.strftime('%H:%M')
            data_str = self.tournament.data.strftime('%d/%m')
        else:
            dia_semana = 'DIA'
            hora_str = '--:--'
            data_str = '--/--'
        
        # Caixa com dia e hora
        self.draw.rectangle(
            [30, y, self.WIDTH - 30, y + 80],
            fill=self.theme['card_bg'],
            outline=self.theme['primary'],
            width=3
        )
        
        self.draw.text(
            (self.WIDTH // 2, y + 25),
            dia_semana.upper(),
            fill=self.theme['primary'],
            font=self._get_font(42, bold=True),
            anchor="mm"
        )
        
        self.draw.text(
            (self.WIDTH // 2, y + 60),
            f"{hora_str} - {data_str}",
            fill=self.theme['secondary'],
            font=self._get_font(32, bold=True),
            anchor="mm"
        )
        
        return y + 110
    
    def _add_gtd_premium(self, y):
        """Adiciona GTD com design premium"""
        gtd_height = 200
        
        # Fundo com borda
        self.draw.rectangle(
            [20, y, self.WIDTH - 20, y + gtd_height],
            fill=self.theme['primary'],
            outline=self.theme['accent'],
            width=4
        )
        
        # Sombra inferior
        self.draw.rectangle(
            [25, y + gtd_height - 5, self.WIDTH - 25, y + gtd_height],
            fill=(0, 0, 0, 100)
        )
        
        gtd_value = f"R$ {float(self.tournament.buyin):,.0f}" if self.tournament.buyin else "TBD"
        
        self.draw.text(
            (self.WIDTH // 2, y + 60),
            gtd_value,
            fill=self.theme['bg'],
            font=self._get_font(90, bold=True),
            anchor="mm"
        )
        
        self.draw.text(
            (self.WIDTH // 2, y + 150),
            "GARANTIDO",
            fill=self.theme['bg'],
            font=self._get_font(32, bold=True),
            anchor="mm"
        )
        
        return y + gtd_height + 25
    
    def _add_info_boxes(self, y):
        """Adiciona caixas de informações de forma mais atrativa"""
        options = []
        
        if self.tournament.buyin:
            options.append(('BUY-IN', f"R$ {float(self.tournament.buyin):.0f}", f"{self.tournament.buyin_chips}K"))
        
        if self.tournament.permite_rebuy and self.tournament.rebuy_valor:
            options.append(('REBUY', f"R$ {float(self.tournament.rebuy_valor):.0f}", f"{self.tournament.rebuy_chips}K"))
        
        if self.tournament.permite_rebuy_duplo and self.tournament.rebuy_duplo_valor:
            options.append(('REBUY 2X', f"R$ {float(self.tournament.rebuy_duplo_valor):.0f}", f"{self.tournament.rebuy_duplo_chips}K"))
        
        if self.tournament.permite_addon and self.tournament.addon_valor:
            options.append(('ADD-ON', f"R$ {float(self.tournament.addon_valor):.0f}", f"{self.tournament.addon_chips}K"))
        
        if self.tournament.staff_valor:
            options.append(('STAFF', f"R$ {float(self.tournament.staff_valor):.0f}", f"{self.tournament.staff_chips}K"))
        
        if not options:
            return y
        
        # Grid: 2 ou 3 colunas dependendo da altura
        cols = 2 if self.template == 'story' else 3
        box_w = (self.WIDTH - 60) // cols - 5
        box_h = 110
        
        for idx, (label, valor, fichas) in enumerate(options):
            col = idx % cols
            row = idx // cols
            
            x = 30 + col * (box_w + 10)
            box_y = y + row * (box_h + 10)
            
            # Box com gradiente
            self.draw.rectangle(
                [x, box_y, x + box_w, box_y + box_h],
                fill=self.theme['card_bg'],
                outline=self.theme['primary'],
                width=2
            )
            
            # Label em ouro
            self.draw.text(
                (x + box_w // 2, box_y + 15),
                label,
                fill=self.theme['primary'],
                font=self._get_font(18, bold=True),
                anchor="mm"
            )
            
            # Valor grande
            self.draw.text(
                (x + box_w // 2, box_y + 45),
                valor,
                fill=self.theme['secondary'],
                font=self._get_font(24, bold=True),
                anchor="mm"
            )
            
            # Fichas pequeno
            self.draw.text(
                (x + box_w // 2, box_y + 80),
                fichas,
                fill=self.theme['text_light'],
                font=self._get_font(14),
                anchor="mm"
            )
        
        rows = (len(options) + cols - 1) // cols
        return y + rows * (box_h + 10)
    
    def _add_extra_info(self, y):
        """Adiciona informações extras (blind, jackpot, regras)"""
        # BLIND STRUCTURE
        self.draw.text(
            (self.WIDTH // 2, y),
            "BLIND STRUCTURE",
            fill=self.theme['primary'],
            font=self._get_font(26, bold=True),
            anchor="mm"
        )
        
        if self.tournament.blind_structure:
            blind_text = f"Níveis de {self.tournament.blind_structure.level_duration}min"
        else:
            blind_text = "Estrutura no painel"
        
        self.draw.text(
            (self.WIDTH // 2, y + 40),
            blind_text,
            fill=self.theme['text_light'],
            font=self._get_font(16),
            anchor="mm"
        )
        
        # Separador
        self.draw.line(
            [(50, y + 70), (self.WIDTH - 50, y + 70)],
            fill=self.theme['primary'],
            width=2
        )
        
        return y + 110
    
    def _add_footer_info(self, y):
        """Adiciona informações de contato no rodapé"""
        # Nome do torneio em destaque
        self.draw.text(
            (self.WIDTH // 2, y),
            self.tournament.nome.upper(),
            fill=self.theme['primary'],
            font=self._get_font(28, bold=True),
            anchor="mm"
        )
        
        self.draw.text(
            (self.WIDTH // 2, y + 50),
            "Para inscrições e mais informações",
            fill=self.theme['text_light'],
            font=self._get_font(16),
            anchor="mm"
        )
        
        return y + 100
    
    def generate_story(self):
        """Gera poster para Story (vertical chamativo)"""
        self._create_background()
        
        y = self._add_title_story()
        y = self._add_gtd_premium(y)
        y = self._add_info_boxes(y)
        y = self._add_extra_info(y)
        y = self._add_footer_info(y)
        
        return self.image
    
    def generate_feed(self):
        """Gera poster para Feed"""
        self._create_background()
        
        # Título
        if self.tournament.data:
            hora_str = self.tournament.data.strftime('%H:%M')
        else:
            hora_str = '--:--'
        
        self.draw.text(
            (self.WIDTH // 2, 40),
            hora_str,
            fill=self.theme['primary'],
            font=self._get_font(56, bold=True),
            anchor="mm"
        )
        
        y = 110
        y = self._add_gtd_premium(y)
        y = self._add_info_boxes(y)
        y = self._add_extra_info(y)
        y = self._add_footer_info(y)
        
        return self.image
    
    def generate_horizontal(self):
        """Gera poster horizontal (landscape)"""
        self._create_background()
        
        # Título à esquerda
        if self.tournament.data:
            hora_str = self.tournament.data.strftime('%H:%M')
        else:
            hora_str = '--:--'
        
        self.draw.text(
            (self.WIDTH // 4, 100),
            "TORNEIO",
            fill=self.theme['primary'],
            font=self._get_font(48, bold=True),
            anchor="mm"
        )
        
        self.draw.text(
            (self.WIDTH // 4, 180),
            hora_str,
            fill=self.theme['secondary'],
            font=self._get_font(64, bold=True),
            anchor="mm"
        )
        
        # GTD à direita
        gtd_x = (self.WIDTH // 4) * 3
        gtd_value = f"R$ {float(self.tournament.buyin):,.0f}" if self.tournament.buyin else "TBD"
        
        self.draw.rectangle(
            [gtd_x - 200, 40, gtd_x + 200, 220],
            fill=self.theme['primary'],
            outline=self.theme['accent'],
            width=3
        )
        
        self.draw.text(
            (gtd_x, 90),
            gtd_value,
            fill=self.theme['bg'],
            font=self._get_font(56, bold=True),
            anchor="mm"
        )
        
        self.draw.text(
            (gtd_x, 180),
            "GARANTIDO",
            fill=self.theme['bg'],
            font=self._get_font(22, bold=True),
            anchor="mm"
        )
        
        # Opções embaixo
        y = 280
        y = self._add_info_boxes(y)
        
        return self.image
    
    def generate(self):
        """Gera a imagem baseada no template"""
        if self.template == 'story':
            return self.generate_story()
        elif self.template == 'horizontal':
            return self.generate_horizontal()
        else:
            return self.generate_feed()
    
    def save(self, filepath):
        """Salva a imagem"""
        if self.image is None:
            self.generate()
        
        self.image.save(filepath, quality=95)
        return filepath
    
    def get_bytes(self):
        """Retorna a imagem como bytes"""
        if self.image is None:
            self.generate()
        
        img_bytes = BytesIO()
        self.image.save(img_bytes, format='PNG', quality=95)
        img_bytes.seek(0)
        return img_bytes

