import React, { MouseEventHandler } from "react";

import {
  Box,
  Button,
  ButtonGroup,
  Heading,
  Icon,
  Popover,
  PopoverArrow,
  PopoverCloseButton,
  PopoverContent,
  PopoverTrigger,
  Stack,
  useDisclosure,
} from "@chakra-ui/react";
import { DeleteIcon } from "@chakra-ui/icons";

type ConfirmDeleteProps = {
  onCancel: MouseEventHandler<HTMLButtonElement>;
  onSubmit: MouseEventHandler<HTMLButtonElement>;
};

const ConfirmDelete: React.FunctionComponent<ConfirmDeleteProps> = (
  props: ConfirmDeleteProps
) => {
  return (
    <Box>
      <Heading>Are you sure ?</Heading>
      <Stack padding={4} spacing={4}>
        <ButtonGroup display="flex" justifyContent="flex-end">
          <Button variant="outline" onClick={props.onCancel}>
            Cancel
          </Button>
          <Button colorScheme="red" onClick={props.onSubmit}>
            Confirm Deletion
          </Button>
        </ButtonGroup>
      </Stack>
    </Box>
  );
};

type DeletePopoverFormProps = {
  button_label: string;
  onSubmit: MouseEventHandler<HTMLButtonElement>;
};

export const DeletePopoverForm: React.FunctionComponent<
  DeletePopoverFormProps
> = (props: DeletePopoverFormProps) => {
  const { onOpen, onClose, isOpen } = useDisclosure();
  const firstFieldRef = React.useRef(null);

  return (
    <>
      <Popover
        isOpen={isOpen}
        initialFocusRef={firstFieldRef}
        onOpen={onOpen}
        onClose={onClose}
        placement="right"
        closeOnBlur={false}
      >
        <PopoverTrigger>
          <Button colorScheme="red">
            <Icon as={DeleteIcon} marginEnd={2} />
            {props.button_label}
          </Button>
        </PopoverTrigger>
        <PopoverContent p={25}>
          <PopoverArrow />
          <PopoverCloseButton />
          <ConfirmDelete onCancel={onClose} onSubmit={props.onSubmit} />
        </PopoverContent>
      </Popover>
    </>
  );
};
