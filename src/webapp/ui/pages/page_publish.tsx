import React from "react";
import {
  Box,
  Button,
  Checkbox,
  CheckboxGroup,
  Icon,
  Popover,
  PopoverBody,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  Portal,
  Stack,
  useDisclosure,
} from "@chakra-ui/react";
import { SunIcon } from "@chakra-ui/icons";
import { ApiError, ApiResult } from "../../casualcms/domain/ports";
import { useConfig } from "../../config";
import { PartialSite } from "../../casualcms/domain/model";
import { Loader } from "../layout/loader";

type PublishButtonProps = {
  token: string;
  pagePath: string;
};

type selectableHostname = {
  hostname: string;
  selected: boolean;
  response?: ApiResult<boolean>;
};

type SiteCheckBoxProps = {
  hostname: selectableHostname;
};

type SiteListBoxProps = {
  hostnames: selectableHostname[];
  onSubmit: React.MouseEventHandler<HTMLButtonElement>;
};

export const SiteListBox: React.FunctionComponent<SiteListBoxProps> = (
  props: SiteListBoxProps
) => {
  const { hostnames, onSubmit } = props;
  return (
    <>
      <CheckboxGroup>
        <Stack marginBottom={5} spacing={[5, 15]} direction={["column"]}>
          {hostnames.map((hostname, i) => (
            <SiteCheckBox key={i} hostname={hostname} />
          ))}
        </Stack>
      </CheckboxGroup>
      <Button colorScheme="teal" onClick={onSubmit} role="publish">
        Submit
      </Button>
    </>
  );
};

type PublishResultBoxProps = {
  hostnames: selectableHostname[];
  onClose: React.MouseEventHandler<HTMLButtonElement>;
};

export const PublishResultBox: React.FunctionComponent<
  PublishResultBoxProps
> = (props: PublishResultBoxProps) => {
  const { hostnames, onClose } = props;
  return (
    <Box>
      {hostnames.map((hostname, i) => (
        <Box key={i}>
          {
            {
              true: (
                <>
                  {hostname.hostname}
                  &nbsp;
                  {hostname.response && hostname.response.isOk() && "OK" || "ERROR"}
                </>
              ),
              false: (
                <>
                  {hostname.hostname}
                  &nbsp; ignored
                </>
              ),
            }[hostname.selected.toString()]
          }
        </Box>
      ))}
      <Button colorScheme="teal" onClick={onClose} role="close_publish_popover">
        Close
      </Button>
    </Box>
  );
};

export const SiteCheckBox: React.FunctionComponent<SiteCheckBoxProps> = (
  props: SiteCheckBoxProps
) => {
  const { hostname } = props;
  return (
    <Checkbox
      value={hostname.hostname}
      colorScheme={"teal"}
      onChange={(e) => {
        hostname.selected = e.target.checked;
      }}
      isChecked={hostname.selected}
    >
      {hostname.hostname}
    </Checkbox>
  );
};

export const PublishButton: React.FunctionComponent<PublishButtonProps> = (
  props: PublishButtonProps
) => {
  const { token, pagePath } = props;
  const { onOpen, onClose, isOpen } = useDisclosure();
  const [publishedState, setPublishedState] = React.useState<
    "loading" | "begin" | "done"
  >("loading");
  const [error, setError] = React.useState<ApiError>(null);
  const [hostnames, setHostnames] = React.useState<selectableHostname[]>([]);
  const config = useConfig();
  const onSubmit = async () => {
    const pages = hostnames
      .filter((el) => el.selected)
      .map((el) => config.api.page.publishPage(token, el.hostname, pagePath));
    const resps = await Promise.all(pages);
    hostnames
      .filter((el) => el.selected)
      .map((el) => (el.response = resps.shift()));
    setPublishedState("done");
  };
  React.useEffect(() => {
    async function loadSites() {
      let sites: ApiResult<PartialSite[]>;
      sites = await config.api.site.listSites(token);
      const hostnamesLoaded = [];
      sites
        .map((sites: PartialSite[]) => {
          sites
            .filter((el) => pagePath.startsWith(el.root_page_path))
            .map((el) =>
              hostnamesLoaded.push({ hostname: el.hostname, selected: false })
            );
        })
        .mapErr((err: ApiError) => setError(err)); // FIXME
      setPublishedState("begin");
      setHostnames(hostnamesLoaded);
    }
    if (token && publishedState == "loading") {
      loadSites();
    }
    return function cleanup() { };
  }, [token, publishedState]);

  return (
    <Popover
      isOpen={isOpen}
      onOpen={() => {
        setPublishedState("loading");
        onOpen();
      }}
      onClose={onClose}
      placement="right"
    >
      <PopoverTrigger>
        <Button colorScheme="teal" role="open_publish_popover">
          <Icon as={SunIcon} marginEnd={2} />
          Publish
        </Button>
      </PopoverTrigger>
      <Portal>
        <PopoverContent backgroundColor={"teal.200"}>
          <PopoverHeader>
            {
              {
                loading: "Choose website(s)",
                begin: "Choose website(s)",
                done: "Publish Reports",
              }[publishedState]
            }
          </PopoverHeader>
          <PopoverCloseButton />
          <PopoverBody>
            {
              {
                loading: (
                  <Loader label="Loading sites" />
                ),
                begin: (
                  <SiteListBox hostnames={hostnames} onSubmit={onSubmit} />
                ),
                done: (
                  <PublishResultBox hostnames={hostnames} onClose={onClose} />
                ),
              }[publishedState]
            }
          </PopoverBody>
        </PopoverContent>
      </Portal>
    </Popover>
  );
};
export const PageEditButtons: React.FunctionComponent<PublishButtonProps> = (
  props: PublishButtonProps
) => {
  return (
    <Stack p={4} spacing={4} direction="row" align="right">
      <PublishButton token={props.token} pagePath={props.pagePath} />
    </Stack>
  );
};
