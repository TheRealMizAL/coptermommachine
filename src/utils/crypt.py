import asyncio
from typing import Tuple, List

import numpy as np
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from passlib.context import CryptContext

app_ctx = CryptContext(schemes=['pbkdf2_sha512', 'pbkdf2_sha256', 'bcrypt'])


class AsyncShamirSecretSharing:
    def __init__(self, prime: int = 2 ** 127 - 1):
        """
        Инициализация с большим простым числом (по умолчанию 2^127 - 1)
        """
        self.prime = prime

    async def _generate_polynomial(self, secret: int, degree: int = 1) -> List[int]:
        """
        Генерация случайного полинома степени degree с заданным секретом
        """
        # Коэффициенты полинома (secret - свободный член)
        coefficients = [secret] + [np.random.randint(1, self.prime) for _ in range(degree)]
        return coefficients

    async def _evaluate_polynomial(self, coefficients: List[int], x: int) -> int:
        """
        Вычисление значения полинома в точке x
        """
        result = 0
        for coefficient in reversed(coefficients):
            result = (result * x + coefficient) % self.prime
        return result

    async def _lagrange_interpolation(self, x: int, shares: List[Tuple[int, int]]) -> int:
        """
        Интерполяция Лагранжа для восстановления секрета
        """
        secret = 0
        for j, (xj, yj) in enumerate(shares):
            # Вычисление лагранжевого базисного полинома l_j(x)
            lj = 1
            for m, (xm, _) in enumerate(shares):
                if m != j:
                    lj = (lj * (x - xm) * pow(xj - xm, -1, self.prime)) % self.prime
            secret = (secret + yj * lj) % self.prime
        return secret

    async def split_secret(self, secret: bytes, num_shares: int = 3, threshold: int = 2) -> List[Tuple[int, bytes]]:
        """
        Разделение секрета на num_shares частей, threshold требуется для восстановления
        """
        # Преобразование секрета в целое число
        secret_int = int.from_bytes(secret, byteorder='big')

        # Генерация полинома
        coefficients = await self._generate_polynomial(secret_int, degree=threshold - 1)

        # Генерация долей
        shares = []
        for i in range(1, num_shares + 1):
            x = i  # ID доли
            y = await self._evaluate_polynomial(coefficients, x)
            shares.append((x, y.to_bytes((y.bit_length() + 7) // 8, byteorder='big')))

        return shares

    async def reconstruct_secret(self, shares: List[Tuple[int, bytes]]) -> bytes:
        """
        Восстановление секрета из долей
        """
        # Преобразование долей в целые числа
        int_shares = [(x, int.from_bytes(y, byteorder='big')) for x, y in shares]

        # Интерполяция Лагранжа для x=0
        secret_int = await self._lagrange_interpolation(0, int_shares)

        return secret_int.to_bytes((secret_int.bit_length() + 7) // 8, byteorder='big')

    async def generate_random_key(self, key_length: int = 32) -> bytes:
        """
        Генерация случайного ключа заданной длины
        """
        return await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: HKDF(
                        algorithm=hashes.SHA256(),
                        length=key_length,
                        salt=None,
                        info=None,
                        backend=default_backend()
                ).derive(b"random-secret-" + str(np.random.randint(0, (1 << 31) - 1)).encode())
        )


# Пример использования
async def example_usage():
    sss = AsyncShamirSecretSharing()

    # Генерация случайного ключа
    key = await sss.generate_random_key(32)
    print(f"Original key: {key.hex()}")

    # Разделение ключа на 3 части (восстановление по 2)
    shares = await sss.split_secret(key, num_shares=3, threshold=2)
    print(f"\nShares:")
    for i, share in enumerate(shares):
        print(f"Share {i + 1}: (x={share[0]}, y={share[1].hex()})")

    # Восстановление из первых двух долей
    recovered_key = await sss.reconstruct_secret(shares[:2])
    print(f"\nRecovered key: {recovered_key.hex()}")
    print(f"Keys match: {key == recovered_key}")


if __name__ == "__main__":
    asyncio.run(example_usage())
