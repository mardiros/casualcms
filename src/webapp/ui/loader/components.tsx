import { Spinner } from "@chakra-ui/react";

type LoaderProps = {
  label: string;
};

export const Loader: React.FunctionComponent<LoaderProps> = (
  props: LoaderProps
) => {
  return <Spinner label={props.label} />;
};
