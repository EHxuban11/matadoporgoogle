import { FC, useMemo } from 'react';

interface Props {
    relativeDate: string;
}

const soonToDieIdiom = () => {
    const items = [
        'Sentenciado a muerte',
        '¡Que les corten la cabeza!',
        'Estirar la pata',
        'Muerto como un clavo',
        'Está acabado',
        'Expirando',
        'Colgar los tenis',
        'Camino del matadero',
        'Otro que muerde el polvo',
        'Apagar el interruptor',
        'Como un tenedor en el enchufe',
        'Programado para ser eliminado',
        'Ser exterminado',
        'Tirado por el inodoro',
        'Desenchufado',
        'Desapareciendo',
        'Haciendo ¡puf!',
        'Volverse cenizas',
        'Recibir un KO',
        'Quedarse sin energía',
        'Desvaneciéndose en la oscuridad',
        'Flotando boca arriba'
    ];
    
    return items[Math.floor(Math.random() * items.length)];
};

const LeadPhrase: FC<Props> = ({ relativeDate }) => {
    const idiom = useMemo(soonToDieIdiom, []);
    return <span>{`${idiom} in ${relativeDate}, `}</span>;
};

export default LeadPhrase;
