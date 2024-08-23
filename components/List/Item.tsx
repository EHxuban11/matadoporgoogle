import React from 'react';
import dynamic from 'next/dynamic';
import {
  format,
  parseISO,
} from 'date-fns';

import { ProductWithSlug } from 'types/Product';
import Badge from 'components/Badge'; 

// Import Styled Components
import {
  AgeRange,
  ContentContainer,
  Description,
  Icon,
  IconContainer,
  ListItem,
} from './Item.atoms';

export default function Item(props: ProductWithSlug) {

  const dateOpen = parseISO(props.dateOpen);
  const dateClose = parseISO(props.dateClose);

  const isPast = () => {
    return new Date() > new Date(props.dateClose);
  };

  const getIcon = () => {
    return isPast() ? (
      <Icon src='https://static.killedbygoogle.com/com/tombstone.svg' alt="Tombstone" />
    ) : (
      <Icon src='https://static.killedbygoogle.com/com/guillotine.svg' alt="Guillotine" />
    );
  };

  const ageRange = () => {
    const yearOpen = dateOpen.getFullYear();
    const yearClose = dateClose.getFullYear();
    if (!isPast()) {
      const monthClose = format(dateClose, 'LLLL');
      return (
        <AgeRange>
          <time dateTime={props.dateClose} title={`${props.dateClose}`}>
            {monthClose}
            <br />
            {yearClose}
          </time>
        </AgeRange>
      );
    }
    return (
      <AgeRange>
        <time dateTime={props.dateOpen} title={props.dateOpen}>
          {yearOpen}
        </time>
        {' - '}
        <time dateTime={props.dateClose} title={props.dateClose}>
          {yearClose}
        </time>
      </AgeRange>
    );
  };

  return (
    <ListItem>
      <IconContainer>
        {getIcon()}
        {ageRange()}
        <Badge content={props.type} />
      </IconContainer>
      <ContentContainer>
        <h2>
          <a href={props.link} target="_blank" rel="noopener noreferrer">
            {props.name}
          </a>
        </h2>
        <Description>
          {props.description}
        </Description>
      </ContentContainer>
    </ListItem>
  );
}
